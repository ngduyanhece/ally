import enum
from typing import Any, Dict, List, Optional

from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from pydantic import BaseModel
from tqdm import tqdm

from ally.utils.internal_data import InternalDataFrame
from ally.utils.logs import print_text
from ally.utils.retry_parser import RetryWithErrorOutputParser

tqdm.pandas()
	
	
class RuntimeModelType(enum.Enum):
	"""Enumeration for LLM runtime model types."""
	OpenAI = 'OpenAI'
	Transformers = 'Transformers'

class Runtime(BaseModel):
	"""
	Class representing an LLM runtime environment.

	Attributes:
		llm_runtime_type (LLMRuntimeModelType): Type of the LLM runtime. Defaults to OpenAI.
		llm_params (Dict[str, str]): Parameters for the LLM runtime.
	"""
	verbose: bool = False
	llm_params: Dict[str, str] = {}
	_llm: BaseLLM
	_chain: LLMChain
	_llm_prompt_template: str

	class Config:
		arbitrary_types_allowed = True
	
	def _create_chain(self):
		# if self.llm_runtime_model_type.value == RuntimeModelType.OpenAI.value:
		# 	self._llm = ChatOpenAI(
		# 		**self.llm_params
		# 	)
		# elif self.llm_runtime_model_type.value == RuntimeModelType.Transformers.value:
		# 	self._llm = HuggingFacePipeline(
		# 		**self.llm_params
		# 	)
		# else:
		# 	raise NotImplementedError(f'LLM runtime type {self.llm_runtime_model_type} is not implemented.')
		# self._chain = LLMChain(
		# 	llm=self._llm,
		# 	prompt=self._llm_prompt_template,
		# )
		pass
	
	def _process_record(
		self,
		record,
		chain,
		output_parser=None,
	) -> Dict[str, Any]:
		"""
		Processes a single record using langchain chain
		 Args:
			record (dict or InternalDataFrame): The record to be processed.
			chain (callable): The langchain chain for processing.
			output_parser: the output parser
			outputs (list of str, optional): Specific output fields to extract from the result.

		Returns:
			dict: Processed output for the record.
		"""
		if not isinstance(record, dict):
			record = record.to_dict()
		else:
			record = record.copy()
		verified_input = record
		# exclude guidance parameter from input
		if self.verbose:
			print_text(str(verified_input))
		result = chain.run(
				verified_input
		)
		# TODO fix the output parser later
		if output_parser is None:
			verified_output = {'output': str(result)}
		else:
			try:
				verified_output = output_parser.parse(result)
			except Exception as e:
				try:
					retry_parser = RetryWithErrorOutputParser.from_llm(
						parser=output_parser, llm=self._llm, max_retries=1)
					verified_output = retry_parser.parse_with_chat_prompt_template(
						result, self._llm_prompt_template, verified_input)
				except Exception as e:
						verified_output = {'output': str(result)}
		return verified_output
	
	def get_input_prompt(self, input_template: str) -> HumanMessagePromptTemplate:
		"""Generates an input prompt from the provided template.

		Args:
			input_template (str): Template to generate the input program.

		Returns:
			HumanMessagePromptTemplate: a prompt template for the human message that input to the agent
		"""
		return HumanMessagePromptTemplate.from_template(input_template)
	
	def get_output_parser(
			self, output_template: List[Dict]) -> StructuredOutputParser:
		"""Generate the output of the agent from the output templates

		Args:
			output_templates (List[Dict]): List of output templates 
			in form of dict {"name": "name", "description": "description"}

		Returns:
			the structure output parser
		"""
		response_schemas = []
		for template in output_template:
			response_schemas.append(ResponseSchema(**template))
		parser = StructuredOutputParser.from_response_schemas(response_schemas)
		format_instructions = parser.get_format_instructions()
		return parser, format_instructions
				
	def get_instruction_prompt(
			self, instruction_template) -> SystemMessagePromptTemplate:
		"""Generates the instruction prompt for the system

		Args:
			instructions_template (str): Template to generate the instruction prompt

		Returns:
			SystemMessagePromptTemplate: template to instruct the agent 
		"""
		return SystemMessagePromptTemplate.from_template(
			instruction_template + "\n{format_instructions}")
	
	def _prepare_chain_and_params(
			self, input_template, output_template, instruction_template):
		output_parser, format_instructions = self.get_output_parser(output_template)
		input_prompt = self.get_input_prompt(input_template)
		instruction_prompt = self.get_instruction_prompt(
			instruction_template)
		self._llm_prompt_template = ChatPromptTemplate(
			messages=[
				input_prompt, instruction_prompt
			],
			partial_variables={"format_instructions": format_instructions}
		)
		self._create_chain()
		return self._chain, output_parser

	def record_to_record(
		self,
		record: Dict[str, Any],
		input_template: str,
		output_template: Optional[str] = None,
		instruction_template: Optional[str] = None,
	) -> Dict[str, Any]:
		"""Processes a record using the provided templates and instructions.

		Args:
			record (Dict[str, Any]): The record data to be processed.
			input_template (str): Template for human message input prompt
			output_template (str): Template for output parser
			instructions (str): Instructions for the system message prompt
		Returns:
				Dict[str, Any]: The processed record.
		"""
		# TODO will fix the output template later
		chain, output_parser = self._prepare_chain_and_params(
			input_template, output_template, instruction_template)
		output = self._process_record(
			record=record,
			chain=chain,
			output_parser=output_parser,
		)
		return output
	
	def batch_to_batch(
		self,
		batch: InternalDataFrame,
		input_template: str,
		output_template: Optional[List[Dict]] = None,
		instruction_template: Optional[str] = None,
	) -> InternalDataFrame:
		"""Processes a batch of records using the provided templates 
		and instructions.

		Args:
				batch (InternalDataFrame): The batch of records to be processed.
				input_template (str): Template for input processing.
				output_template (str): Template for output processing.
				instructions (str): Instructions for guidance.
				during batch processing.

		Returns:
				InternalDataFrame: The processed batch of records.
		"""
		# TODO will fix the output template later		
		chain, output_parser = self._prepare_chain_and_params(
			input_template, output_template, instruction_template)
		output = batch.progress_apply(
				self._process_record,
				axis=1,
				result_type='expand',
				chain=chain,
				output_parser=output_parser,
		)
		return output

	def record_to_batch(
		self,
		record: Dict[str, Any],
		input_template: str,
		output_template: Optional[List[Dict]] = None,
		instruction_template: Optional[str] = None,
		output_batch_size: int = 1
	) -> InternalDataFrame:
		"""
			Processes a record and return a batch.

			Args:
				record (Dict[str, str]): The record to process.
				input_template (str): The input template.
				instructions_template (str): The instructions template.
				output_template (str): The output template.
				instruction_template (str): The instruction template.
				output_batch_size (int): The batch size for the output. Defaults to 1..
			Returns:
				InternalDataFrame: The processed batch.
		"""
		batch = InternalDataFrame([record] * output_batch_size)
		return self.batch_to_batch(
			batch=batch,
			input_template=input_template,
			output_template=output_template,
			instruction_template=instruction_template,
		)

			 
	
