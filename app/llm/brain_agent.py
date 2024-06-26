from typing import ClassVar, Dict, Optional
from uuid import UUID

import pandas as pd
from pydantic import BaseModel
from supabase.client import Client, create_client

from ally.agents.base import Agent
from ally.environments.base import Environment, StaticEnvironment
from ally.runtimes.base import Runtime
from ally.runtimes.openai import OpenAIRuntime
from ally.skills.base import RetrievalSkill, Skill, TransformSkill
from ally.skills.skillset import LinearSkillSet
from ally.utils.internal_data import InternalDataFrame_encoder
from ally.vector_store.base import AllyVectorStore
from app.core.settings import settings
from app.llm.utils.retrieval_input_template_from_a_prompt import (
    get_input_template_from_a_prompt_inout_template,
    retrieval_input_template_from_a_inout_template)
from app.modules.agent.entity.agent import BrainAgentInput
from app.modules.brain.entity.brain import (FullBrainEntityWithRights,
                                            RuntimeType)
from app.modules.chat.entity.chat import (CreateChatHistory,
                                          GetChatHistoryOutput)
from app.modules.chat.service.chat_service import ChatService
from app.modules.prompt.entity.prompt import Prompt
from app.modules.prompt.service.prompt_service import PromptService
from app.vectorstore.supabase import CustomSupabaseVectorStore

prompt_service = PromptService()
chat_service = ChatService()


class BrainAgent(BaseModel):
	"""
	Represents a customizable agent that can interact with environments, 
	employ skills, and leverage memory and runtimes.
	this agent leverage the interface of ally agent
	"""
	class Config:
		"""Configuration of the Pydantic Object"""

		# Allowing arbitrary types for class validation
		arbitrary_types_allowed = True
	# Default class attributes
	brain_settings: ClassVar = settings
	brain_details: FullBrainEntityWithRights
	prompt: Prompt = None
	brain_skill: Skill = None
	input_analyzer_skill: Skill = None
	output_analyzer_skill: Skill = None
	supabase_client: Optional[Client] = None
	vector_store: Optional[AllyVectorStore] = None
	runtime: Runtime = None
	teacher_runtime: Runtime = None
	runtime_name: str = None
	teacher_runtime_name: str = None
	environment: Environment = None

	def _create_supabase_client(self) -> Client:
		return create_client(
				self.brain_settings.supabase_url,
				self.brain_settings.supabase_service_key
		)
	
	def _create_vector_store(self, embeddings) -> AllyVectorStore:
		vector_store = CustomSupabaseVectorStore(
				self.supabase_client,
				embeddings,
				table_name="vectors",
				brain_id=self.brain_details.id,
		)
		return AllyVectorStore(vector_store=vector_store)

	def _get_prompt_to_use(self) -> Prompt:
		return prompt_service.get_prompt_by_id(self.brain_details.prompt_id)
	
	def _create_runtime(self, runtime_type: str = 'student') -> Dict[str, Runtime]:
		if runtime_type == 'student':
			brain_runtime = self.brain_details.runtime
		elif runtime_type == 'teacher':
			brain_runtime = self.brain_details.teacher_runtime
		else:
			raise NotImplementedError
		if brain_runtime.type == RuntimeType.OpenAi:
			target_runtime = OpenAIRuntime(
				gpt_model_name=brain_runtime.model,
				max_tokens=brain_runtime.max_tokens,
				temperature=brain_runtime.temperature,
				api_key=brain_runtime.openai_api_key,
			)
		elif brain_runtime.type == RuntimeType.HuggingFace:
				raise NotImplementedError
		else:
			raise NotImplementedError
		return target_runtime, brain_runtime.name
		
	def _create_brain_skill(
			self,
			prompt: Prompt,
			vector_store: CustomSupabaseVectorStore) -> Skill:
		input_template = retrieval_input_template_from_a_inout_template(
			prompt.input_template)
		return RetrievalSkill(
			name=self.brain_details.name,
			description=self.brain_details.description,
			instruction_template=prompt.content,
			input_template=input_template,
			output_template=[dict(template) for template in prompt.output_template],
			vector_store=vector_store,
			query_input_fields=[template.name for template in prompt.input_template],
			query_output_field="context",
		)
	
	def _create_input_analyzer_skill(self, output_template):
		"""
		this is the build-in skill, this skill get the input from the user, output the skill sequence and 
		the input for the next skill
		"""
		return TransformSkill(
			name='input_analyzer',
			instruction_template="your task is to condense the chat input and the chat history \
				to output the intend of user",
			input_template="chat input: {text_input} and chat history: {chat_history}",
			output_template=output_template
		)
	
	def _create_output_analyzer_skill(self, input_template):
		"""
		this is the build-in skill, this skill get the output from the last skill,
		this will concatenate all the output from the last skill and output the 
		result. this is used for learning purpose only
		"""
		return TransformSkill(
			name='output_analyzer',
			instruction_template="your task is to concatenate all the output from the last skill and output the single result",
			input_template=get_input_template_from_a_prompt_inout_template(input_template),
			output_template=[
				{
					"name": "final_prediction",
					"description": "the final prediction from the last skill",
				}
			]
		)
	
	def _create_environment(self, df, matching_threshold=0.9) -> Environment:
		return StaticEnvironment(
			df=df,
			ground_truth_columns={"output": "reference_output"},
			matching_threshold=matching_threshold
		)
	
	# def _add_experience_to_agent(
	# 	self, vector_store: AllyVectorStore, experience: str):
	# 	file_sha1 = compute_sha1_from_string(experience)
	# 	experience_doc = Document(
	# 		page_content=experience,
	# 		metadata={
	# 			"brain_name": self.brain_details.name,
	# 			"file_sha1": file_sha1,
	# 		}
	# 	)
	# 	created_vector = vector_store.update(experience_doc)
	# 	created_vector_id = created_vector[0]
	# 	brain = Brain(id=self.brain_details.brain_id)
	# 	brain.create_brain_vector(created_vector_id, file_sha1)
	# 	database = get_supabase_db()
	# 	database.set_file_sha_from_metadata(file_sha1)
		
	def __init__(self, brain_details: FullBrainEntityWithRights, **data):
		super().__init__(
			brain_details=brain_details,
			**data
		)
		self.supabase_client = self._create_supabase_client()
		self.prompt = self._get_prompt_to_use()
		self.runtime, self.runtime_name = self._create_runtime(runtime_type='student')
		self.vector_store = self._create_vector_store(
			self.runtime.get_embeddings())
		self.brain_skill = self._create_brain_skill(self.prompt, self.vector_store)
		self.input_analyzer_skill = self._create_input_analyzer_skill(
			output_template=[dict(template) for template in self.prompt.input_template]
		)
		
	def generate_answer(
		self, chat_id: UUID, input: BrainAgentInput
	) -> GetChatHistoryOutput:
		"""Generate an answer to a question"""
		agent = Agent(
			skills=LinearSkillSet(
				skills=[self.brain_skill],
				skill_sequence=[self.brain_skill.name]
			),
			runtimes={
				self.runtime_name: self.runtime,
			}
		)
		transformed_history = chat_service.format_chat_history(
			chat_service.get_enrich_chat_history(chat_id))
		verified_input = dict(input)
		verified_input["chat_history"] = transformed_history
		verified_input_df = pd.DataFrame([verified_input])
		prediction = InternalDataFrame_encoder(
			agent.run(verified_input_df, self.runtime_name)
		)[0]
		answer = " ".join([prediction[template["name"]] for template in self.brain_skill.output_template])
		new_chat = chat_service.update_chat_history(
			CreateChatHistory(
				**{
						"id": chat_id,
						"user_message": input.text_input,
						"assistant": answer,
						"brain_id": self.brain_details.id,
						"prompt_id": self.brain_details.prompt_id,
				}
			)
		)
		return GetChatHistoryOutput(
			**{
				"chat_id": chat_id,
				"user_message": input.text_input,
				"assistant": answer,
				"message_time": new_chat.message_time,
				"brain_id": str(self.brain_details.id),
				"prompt_id": str(self.brain_details.prompt_id),
				"message_id": new_chat.message_id
			}
		)
	
	# def learn(
	# 	self,
	# 	chat_id: UUID,
	# 	testcase_data_id: UUID,
	# 	update_memory: bool = False
	# ) -> GetChatHistoryOutput:
	# 	"""Learn and improve the brain skill
	# 	from the dataset as the environment
	# 	"""
	# 	raw_dataset = get_testcase_data_by_id(testcase_data_id)
	# 	df_dataset = pd.DataFrame([dict(raw_dataset)])
	# 	self.output_analyzer_skill = self._create_output_analyzer_skill(self.prompt.output_template)
		
	# 	agent = Agent(
	# 		skills=LinearSkillSet(
	# 			skills=[self.brain_skill],
	# 			skill_sequence=[self.brain_skill.name]
	# 		),
	# 		runtimes={
	# 			self.runtime_name: self.runtime,
	# 		}
	# 	)
	# 	agent.environment = self._create_environment(df_dataset)
	# 	self.teacher_runtime, self.teacher_runtime_name = self._create_runtime(runtime_type='teacher')
	# 	agent.teacher_runtimes = {
	# 		self.teacher_runtime_name: self.teacher_runtime
	# 	}
	# 	suggested_prompt, experience = agent.learn(
	# 		learning_iterations=1,
	# 		accuracy_threshold=0.9,
	# 		batch_size=1,
	# 		update_memory=update_memory,
	# 		runtime=self.runtime_name,
	# 		teacher_runtime=self.teacher_runtime_name
	# 	)
		
	# 	if update_memory and experience != "":
	# 		self._add_experience_to_agent(self.vector_store, experience)

	# 	new_chat = update_chat_history(
	# 		CreateChatHistory(
	# 			**{
	# 					"chat_id": chat_id,
	# 					"user_message": raw_dataset.text_input,
	# 					"assistant": "BETTER PROMPT: " + suggested_prompt + "\n REASONING: " + experience,
	# 					"brain_id": self.brain_details.brain_id,
	# 					"prompt_id": self.brain_details.prompt_id,
	# 			}
	# 		)
	# 	)
	# 	return GetChatHistoryOutput(
	# 		**{
	# 			"chat_id": chat_id,
	# 			"user_message": raw_dataset.text_input,
	# 			"assistant": "BETTER PROMPT: " + suggested_prompt + "\n REASONING: " + experience,
	# 			"message_time": new_chat.message_time,
	# 			"brain_id": str(self.brain_details.brain_id),
	# 			"prompt_id": str(self.brain_details.prompt_id),
	# 			"message_id": new_chat.message_id
	# 		}
	# 	)
	
		
