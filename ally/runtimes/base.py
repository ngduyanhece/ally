import enum
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts.chat import (HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from langchain.tools.base import BaseTool
from pydantic import BaseModel
from tqdm import tqdm

from ally.utils.internal_data import InternalDataFrame
from ally.utils.logs import print_text

tqdm.pandas()
	
	
class RuntimeModelType(enum.Enum):
	"""Enumeration for LLM runtime model types."""
	OpenAI = 'OpenAI'
	Transformers = 'Transformers'

class Runtime(BaseModel):
	"""
	Class representing an LLM runtime environment.

	Attributes:
		verbose (bool): Whether to print verbose logs. Defaults to False.
		llm_params (Dict[str, str]): Parameters for the LLM runtime.
	"""
	verbose: bool = False
	llm_params: Dict[str, str] = {}
	_llm: BaseLLM
	_chain: LLMChain
	_llm_prompt_template: str

	class Config:
		arbitrary_types_allowed = True
			
	def get_input_prompt(self, input_template: str) -> HumanMessagePromptTemplate:
		"""Generates an input prompt from the provided template.

		Args:
			input_template (str): Template to generate the input program.

		Returns:
			HumanMessagePromptTemplate: a prompt template for the human message that input to the agent
		"""
		return HumanMessagePromptTemplate.from_template(input_template)
				
	def get_instruction_prompt(
			self, instruction_template) -> SystemMessagePromptTemplate:
		"""Generates the instruction prompt for the system

		Args:
			instructions_template (str): Template to generate the instruction prompt

		Returns:
			SystemMessagePromptTemplate: template to instruct the agent
		"""
		return SystemMessagePromptTemplate.from_template(instruction_template)
	
	def _create_chain(self):
		"""
		Create the chain for the the runtime
		This will be defined clearly for each type of runtime
		"""
		pass
	
	def _prepare_default_llm_tool(
			self, input_template, instruction_template):
		"""
			Prepare the default tool for the agent
			Args:
				input_template (str): Template for human message input prompt
				instructions (str): InstrListuctions for the system message prompt
			Returns:
				the chain
		"""
		input_prompt = self.get_input_prompt(input_template)
		instruction_prompt = self.get_instruction_prompt(
			instruction_template)
		self._llm_prompt_template = ChatPromptTemplate(
			messages=[
				input_prompt, instruction_prompt
			]
		)
		self._create_chain()
		return self._chain
	
	def _prepare_agent_and_tools(
		self,
		input_template: str,
		instruction_template: str,
		default_llm_function_name: str,
		default_llm_function_description: str,
		prefix: str,
		format_instructions: str,
		conversation_buffer_memory: ConversationBufferMemory = None,
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
			# return_direct=True,
		)
		prefix = prefix + "You have access to the following tools:\n"
		if conversation_buffer_memory is not None:
			suffix = "Begin {chat_history}!\n" + input_template + "Thought:{agent_scratchpad}"
		else:
			suffix = "Begin!\n" + input_template + "Thought:{agent_scratchpad}"
		if conversation_buffer_memory is not None:
			agent_executor = initialize_agent(
				tools=[default_tool] + tools,
				llm=self._llm,
				agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
				agent_kwargs={
					"prefix": prefix,
					"format_instructions": format_instructions,
					"extra_prompt_messages": [
						MessagesPlaceholder(variable_name="chat_history")],
					"suffix": suffix
				},
				memory=conversation_buffer_memory,
				handle_parsing_errors=True,
				trim_intermediate_steps=-1,
				return_intermediate_steps=self.verbose,
				early_stopping_method="force",
			)
		else:
			agent_executor = initialize_agent(
				tools=[default_tool] + tools,
				llm=self._llm,
				agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
				agent_kwargs={
					"prefix": prefix,
					"format_instructions": format_instructions,
					"extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")],
					"suffix": suffix
				},
				handle_parsing_errors=True,
				trim_intermediate_steps=-1,
				return_intermediate_steps=self.verbose,
				early_stopping_method="force",
			)
		return agent_executor
	
	def _process_record(
		self,
		record,
		agent_executor
	) -> Dict[str, Any]:
		"""
		Processes a single record using langchain chain
			Args:
			record (dict or InternalDataFrame): The record to be processed.
			agent_executor (callable): The langchain agent executor for processing.
		Returns:
			dict: Processed output for the record.
		"""
		if not isinstance(record, dict):
			record = record.to_dict()
		else:
			record = record.copy()
		verified_input = record
		if self.verbose:
			print_text(str(verified_input))
		result = agent_executor.invoke(
				verified_input
		)
		# print_text("agent result is")
		# print(result)
		return result

	def record_to_record(
		self,
		record: Dict[str, Any],
		input_template: str,
		instruction_template: str,
		default_llm_function_name: str,
		default_llm_function_description: str,
		prefix: str,
		format_instructions: str,
		conversation_buffer_memory: ConversationBufferMemory,
		tools: Optional[List[BaseTool]] = [],
	) -> Dict[str, Any]:
		"""Processes a record using the provided templates and instructions.
		 Args:
			record (Dict[str, str]): The record to process.
			input_template (str): Template for input processing.
			instruction_template (str): Template for instruction
			default_llm_function_name (str): The default function name
			default_llm_function_description (str): The description for the default function
			prefix (str): The prefix for the agent
			format_instructions (str): The format instructions for the agent
			tools (list[Tool]): The list of tools for the agent
		"""
		agent_executor = self._prepare_agent_and_tools(
			input_template,
			instruction_template,
			default_llm_function_name,
			default_llm_function_description,
			prefix,
			format_instructions,
			conversation_buffer_memory,
			tools
		)
		output = self._process_record(record, agent_executor)
		return output
	
	def batch_to_batch(
		self,
		batch: InternalDataFrame,
		input_template: str,
		instruction_template: str,
		default_llm_function_name: str,
		default_llm_function_description: str,
		prefix: str,
		format_instructions: str,
		conversation_buffer_memory: ConversationBufferMemory,
		tools: Optional[List[BaseTool]] = [],
	) -> InternalDataFrame:
		"""Processes a batch of records using the provided templates 
		and instructions.

		Args:
			batch (InternalDataFrame): The batch of records to be processed.
			input_template (str): Template for input processing.
			instruction_template (str): Template for instruction
			default_llm_function_name (str): The default function name
			default_llm_function_description (str): The description for the default function
			prefix (str): The prefix for the agent
			format_instructions (str): The format instructions for the agent
			tools (list[Tool]): The list of tools for the agent
		Returns:
				InternalDataFrame: The processed batch of records.
		"""
		agent_executor = self._prepare_agent_and_tools(
			input_template,
			instruction_template,
			default_llm_function_name,
			default_llm_function_description,
			prefix,
			format_instructions,
			conversation_buffer_memory,
			tools
		)

		output = batch.progress_apply(
			self._process_record,
			axis=1,
			result_type='expand',
			agent_executor=agent_executor,
		)
		return output

	def record_to_batch(
		self,
		record: Dict[str, Any],
		input_template: str,
		instruction_template: str,
		default_llm_function_name: str,
		default_llm_function_description: str,
		prefix: str,
		format_instructions: str,
		tools: Optional[List[BaseTool]] = [],
		output_batch_size: int = 1
	) -> InternalDataFrame:
		"""
			Processes a record and return a batch.

			Args:
				record (Dict[str, str]): The record to process.
				input_template (str): Template for input processing.
				instruction_template (str): Template for instruction
				default_llm_function_name (str): The default function name
				default_llm_function_description (str): The description for the default function
				prefix (str): The prefix for the agent
				format_instructions (str): The format instructions for the agent
				tools (list[Tool]): The list of tools for the agent
				output_batch_size (int): The batch size for the output. Defaults to 1..
			Returns:
				InternalDataFrame: The processed batch.
		"""
		batch = InternalDataFrame([record] * output_batch_size)

		return self.batch_to_batch(
			batch=batch,
			input_template=input_template,
			instruction_template=instruction_template,
			default_llm_function_name=default_llm_function_name,
			default_llm_function_description=default_llm_function_description,
			prefix=prefix,
			format_instructions=format_instructions,
			tools=tools,
		)

			 
	
