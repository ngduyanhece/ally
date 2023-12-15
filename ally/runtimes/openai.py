from typing import Any, List, Optional

import openai
from langchain.agents import AgentExecutor, Tool
from langchain.agents.load_tools import load_tools
from langchain.agents.openai_assistant.base import (OpenAIAssistantRunnable,
                                                    _get_openai_client)
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_core.tools import BaseTool

from ally.runtimes.base import Runtime, SkillEntity
from ally.tools.load_tools import load_tool_kit
from ally.utils.logs import print_text


class OpenAIRuntime(Runtime):
	"""Runtime class specifically designed for OpenAI models.

	This class is tailored to use OpenAI models, particularly GPT models.
	It inherits from the `LLMRuntime` class and thus can utilize its functionalities but specializes 
	for the OpenAI ecosystem.

	Attributes:
		api_key (str): The API key required to access OpenAI's API.
		gpt_model_name (str): Name of the GPT model. Defaults to 'gpt-3.5-turbo-instruct'.
		temperature (float): Sampling temperature for the GPT model's output. 
													A higher value makes output more random, while a lower value makes it more deterministic.
													Defaults to 0.0.
	"""
		
	api_key: Optional[str] = None
	gpt_model_name: Optional[str]
	temperature: Optional[float] = 0.0
	max_tokens: Optional[int] = 256

	def __init__(
		self,
		api_key: str,
		gpt_model_name: str,
		temperature: float = 0.0,
		max_tokens: int = 256,
		**kwargs,
	):
		super().__init__(
			api_key=api_key,
			gpt_model_name=gpt_model_name,
			temperature=temperature,
			max_tokens=max_tokens,
			**kwargs,
		)
		# self._check_api_key()
		# self._check_model_availability()
		self.llm_params = {
			'model_name': self.gpt_model_name,
			'temperature': self.temperature,
			'openai_api_key': self.api_key,
			'max_tokens': self.max_tokens,
		}

	# def _check_api_key(self):
	# 	if self.api_key:
	# 		return
	# 	self.api_key = os.getenv('OPENAI_API_KEY')
	# 	if not self.api_key:
	# 		print_error(
	# 			'OpenAI API key is not provided. Please set the OPENAI_API_KEY environment variable:\n\n'
	# 			'export OPENAI_API_KEY=your-openai-api-key\n\n'
	# 			'or set the `api_key` attribute of the `OpenAIRuntime` python class:\n\n'
	# 			f'{self.__class__.__name__}(..., api_key="your-openai-api-key")\n\n'
	# 			f'Read more about OpenAI API keys at https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key')
	# 		raise ValueError('OpenAI API key is not provided.')

	# def _check_model_availability(self):
	# 	models = openai.Model.list(api_key=self.api_key)
	# 	models = set(model['id'] for model in models['data'])
	# 	if self.gpt_model_name not in models:
	# 		print_error(
	# 			f'Requested model "{self.gpt_model_name}" is not available in your OpenAI account. '
	# 			f'Available models are: {models}\n\n'
	# 			f'Try to change the runtime settings for {self.__class__.__name__}, for example:\n\n'
	# 			f'{self.__class__.__name__}(..., model="gpt-3.5-turbo")\n\n')
	# 		raise ValueError(f'Requested model {self.gpt_model_name} is not available in your OpenAI account.')
		
	def _create_chain(self):
		self._llm = ChatOpenAI(
			**self.llm_params
		)
		self._chain = LLMChain(
			llm=self._llm,
			prompt=self._llm_prompt_template,
		)

	def get_embeddings(self) -> OpenAIEmbeddings:
		"""Get the embeddings of the model."""
		return OpenAIEmbeddings(
			openai_api_key=self.llm_params["openai_api_key"],
		)
	

class CustomOpenAIAssistantRunnable(OpenAIAssistantRunnable):
	class Config:
		arbitrary_types_allowed = True
  	
	@classmethod
	def check_if_assistant_exist(self, assistant_id: str):
		agent = self.client.beta.assistants.retrieve(assistant_id)
		return agent is not None
	
	@classmethod
	def retrieve_assistant(
		cls,
		assistant_id: str,
		*,
		client: Optional[openai.OpenAI] = None,
		**kwargs: Any,
	) -> OpenAIAssistantRunnable:
			"""Create an OpenAI Assistant and instantiate the Runnable.

			Args:
					name: Assistant name.
					instructions: Assistant instructions.
					tools: Assistant tools. Can be passed in in OpenAI format or as BaseTools.
					model: Assistant model to use.
					client: OpenAI client. Will create default client if not specified.

			Returns:
					OpenAIAssistantRunnable configured to run using the created assistant.
			"""
			client = client or _get_openai_client()
			assistant = client.beta.assistants.retrieve(assistant_id)
			return cls(assistant_id=assistant.id, **kwargs)

  	
class OpenAIAssistantRuntime(OpenAIRuntime):
	assistant_id: Optional[str] = None

	def _prepare_agent_and_tools(
		self,
		input_template: str,
		instruction_template: str,
		default_llm_function_name: str,
		default_llm_function_description: str,
		assistant_id: Optional[str] = None,
		tools: List[BaseTool] = [],
	) -> AgentExecutor:
		"""
			Prepare the agent and tools for the runtime
			Args:
				input_template (str): Template for human message input prompt
				instructions (str): Instructions for the system message prompt
				default_llm_function_name (str): The default function name
				default_llm_function_description (str): The description for the default function
				prefix (str): The prefix for the agent
				format_instructions (str): The format instructions for the agent
				conversation_buffer_memory (ConversationBufferMemory): The memory for the conversation
				tools (list[Tool]): The list of tools for the agent
			Returns:
				the agent executor
		"""
		default_llm_tool = self._prepare_default_llm_tool(
			input_template, instruction_template
		)
		default_tool = Tool.from_function(
			func=default_llm_tool.run,
			name=default_llm_function_name,
			description=default_llm_function_description,
		)
		if assistant_id is None:
			agent = CustomOpenAIAssistantRunnable.create_assistant(
				name=default_llm_function_name,
				instructions=instruction_template,
				tools=[default_tool] + tools,
				model=self.llm_params["model_name"],
				as_agent=True
			)
		else:
			agent = CustomOpenAIAssistantRunnable.retrieve_assistant(
				assistant_id=assistant_id,
				as_agent=True
			)
		self.assistant_id = agent.assistant_id
		agent_executor = AgentExecutor(agent=agent, tools=tools)
		return agent_executor
	
	def agent_up(
		self,
		skill: SkillEntity
	) -> AgentExecutor:
		print_text("initializing new agent")
		if len(skill.tool_names) > 0:
			tools = load_tools(skill.tool_names, **skill.tool_kwargs)
		else:
			tools = []
		if len(skill.tool_kit_names) > 0:
			tools_from_tool_kits = [load_tool_kit(tool_kit_name) for tool_kit_name in skill.tool_kit_names]
			tools_from_tool_kits = [tool for tool_list in tools_from_tool_kits for tool in tool_list]
			tools.extend(tools_from_tool_kits)
		self.agent_executor = self._prepare_agent_and_tools(
			skill.input_template,
			skill.instruction_template,
			skill.name,
			skill.description,
			skill.assistant_id,
			tools
		)