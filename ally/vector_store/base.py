from typing import Any, Dict

from langchain.schema import Document
from langchain.schema.vectorstore import VectorStore
from pydantic import BaseModel

from ally.utils.internal_data import InternalDataFrame


class AllyVectorStore(BaseModel):
		
	class Config:
		arbitrary_types_allowed = True
	
	vector_store: VectorStore = None

	def update(self, experience_doc: Document):
		ids = self.vector_store.add_documents([experience_doc])
		return ids

	def _process_record(
		self,
		record,
		input_fields: list[str],
	) -> Dict[str, Any]:
		"""Processes a single record using input and output fields.

		Args:
				record (Dict[str, str]): The record to be processed.
				input_field (str): The input field to be used for extract the query.
				output_field (str): The output field to store the result.

		Returns:
				Dict[str, Any]: The processed record.
		"""
		if not isinstance(record, dict):
			record = record.to_dict()
		else:
			record = record.copy()
		input_data = " ".join([str(
			record[input_field]) for input_field in input_fields])
		docs = self.vector_store.similarity_search(input_data)
		# append docs in each input field
		for input_field in input_fields:
				record[input_field] = record[input_field] + f""" this is the related contents:  {docs}"""

		return record

	def batch_to_batch(
		self,
		batch: InternalDataFrame,
		input_fields: list[str],
	) -> InternalDataFrame:
		output = batch.progress_apply(
				self._process_record,
				axis=1,
				result_type='expand',
				input_fields=input_fields,
		)
		return output
		
