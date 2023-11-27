import os
from typing import Optional

import openai
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

from ally.runtimes.base import Runtime
from ally.utils.logs import print_error


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
		self._check_api_key()
		self._check_model_availability()
		self.llm_params = {
			'model_name': self.gpt_model_name,
			'temperature': self.temperature,
			'openai_api_key': self.api_key,
			'max_tokens': self.max_tokens,
		}

	def _check_api_key(self):
		if self.api_key:
			return
		self.api_key = os.getenv('OPENAI_API_KEY')
		if not self.api_key:
			print_error(
				'OpenAI API key is not provided. Please set the OPENAI_API_KEY environment variable:\n\n'
				'export OPENAI_API_KEY=your-openai-api-key\n\n'
				'or set the `api_key` attribute of the `OpenAIRuntime` python class:\n\n'
				f'{self.__class__.__name__}(..., api_key="your-openai-api-key")\n\n'
				f'Read more about OpenAI API keys at https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key')
			raise ValueError('OpenAI API key is not provided.')

	def _check_model_availability(self):
		models = openai.Model.list(api_key=self.api_key)
		models = set(model['id'] for model in models['data'])
		if self.gpt_model_name not in models:
			print_error(
				f'Requested model "{self.gpt_model_name}" is not available in your OpenAI account. '
				f'Available models are: {models}\n\n'
				f'Try to change the runtime settings for {self.__class__.__name__}, for example:\n\n'
				f'{self.__class__.__name__}(..., model="gpt-3.5-turbo")\n\n')
			raise ValueError(f'Requested model {self.gpt_model_name} is not available in your OpenAI account.')
		
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
