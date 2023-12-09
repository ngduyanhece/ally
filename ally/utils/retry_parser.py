from __future__ import annotations

from typing import Any, Dict, List, TypeVar

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import (BaseOutputParser, BasePromptTemplate,
                              OutputParserException)
from langchain.schema.language_model import BaseLanguageModel

T = TypeVar("T")

NAIVE_COMPLETION_RETRY_WITH_ERROR = """Prompt:
{prompt}
Completion:
{completion}

Above, the Completion did not satisfy the constraints given in the Prompt.
Details: {error}
Please try again and do not include any special characters that may cause errors when parsing with json or yaml."""
NAIVE_RETRY_WITH_ERROR_PROMPT = PromptTemplate.from_template(
		NAIVE_COMPLETION_RETRY_WITH_ERROR
)

class RetryWithErrorOutputParser(BaseOutputParser[T]):
		"""Wraps a parser and tries to fix parsing errors.

		Does this by passing the original prompt, the completion, AND the error
		that was raised to another language model and telling it that the completion
		did not work, and raised the given error. Differs from RetryOutputParser
		in that this implementation provides the error that was raised back to the
		LLM, which in theory should give it more information on how to fix it.
		"""

		parser: BaseOutputParser[T]
		"""The parser to use to parse the output."""
		# Should be an LLMChain but we want to avoid top-level imports from langchain.chains
		retry_chain: Any
		"""The LLMChain to use to retry the completion."""
		max_retries: int = 1
		"""The maximum number of times to retry the parse."""

		@classmethod
		def from_llm(
				cls,
				llm: BaseLanguageModel,
				parser: BaseOutputParser[T],
				prompt: BasePromptTemplate = NAIVE_RETRY_WITH_ERROR_PROMPT,
				max_retries: int = 1,
		) -> RetryWithErrorOutputParser[T]:
				"""Create a RetryWithErrorOutputParser from an LLM.

				Args:
						llm: The LLM to use to retry the completion.
						parser: The parser to use to parse the output.
						prompt: The prompt to use to retry the completion.
						max_retries: The maximum number of times to retry the completion.

				Returns:
						A RetryWithErrorOutputParser.
				"""
				from langchain.chains.llm import LLMChain

				chain = LLMChain(llm=llm, prompt=prompt)
				return cls(parser=parser, retry_chain=chain, max_retries=max_retries)

		def parse_with_chat_prompt_template(
				self,
				completion: str,
				chat_prompt_template: ChatPromptTemplate,
				verified_input: dict
		) -> T:
			retries = 0

			while retries <= self.max_retries:
					try:
							return self.parser.parse(completion)
					except OutputParserException as e:
							if retries == self.max_retries:
									return {"output": completion}
							else:
									retries += 1
									completion = self.retry_chain.run(
											prompt=chat_prompt_template.format(**verified_input),
											completion=completion,
											error=repr(e),
									)
			# raise RuntimeError(
			# 		"Unreachable code reached. This is a bug in the RetryWithErrorOutputParser."
			# 	)
		
		def parse(self, completion: str) -> T:
				raise NotImplementedError(
						"This OutputParser can only be called by the `parse_with_prompt` method."
				)

		def get_format_instructions(self) -> str:
				return self.parser.get_format_instructions()

		@property
		def _type(self) -> str:
				return "retry_with_error"

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
