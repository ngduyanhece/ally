

from abc import ABC
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ally.runtimes.base import Runtime
from ally.utils.internal_data import InternalDataFrame, InternalSeries
from ally.utils.logs import print_dataframe
from ally.vector_store.base import AllyVectorStore


class Skill(BaseModel, ABC):
	"""
	A foundational abstract class representing a skill. This class sets the foundation 
	for all skills and provides common attributes and methods for skill-based operations.

	Attributes:
		name (str): Unique name of the skill.
		instruction_template (str): Instructs agent what to do with the input data.
		description (str): Description of the skill.
		input_template (str): Template for the human system input
		output_templates (str): Template for parsing the output
		prediction_field (str): Name of the prediction field to be used for the output data.
	"""
	name: str = Field(
		title='Skill name',
		description='Unique name of the skill',
		default='',
		examples=['labeling', 'classification', 'text-generation']
	)
			
	instruction_template: str = Field(
		title='Skill instructions',
		description='Instructs agent what to do with the input data. '
								'Can use templating to refer to input fields.',
		default='',
		examples=['Label the input text with the following labels: {labels}']
	)
			
	description: str = Field(
		default='',
		title='Skill description',
		description='Description of the skill. Can be used to retrieve skill from the library.',
		examples=['The skill to perform sentiment analysis on the input text.']
	)
	input_template: str = Field(
		title='Input template',
		description='Template for the input data. '
								'Can use templating to refer to input parameters and perform data transformations.',
		default="Input: {input}",
		examples=["Text: {input}, Date: {date_column}, Sentiment: {sentiment}"]
	)
	# TODO: skill can have multiple input fields
	output_template: Optional[List[dict]] = Field(
		title='Output template',
		description='Template for the output data. '
								'Can use templating to refer to input parameters and perform data transformations',
		default=[{"name": "name", "description": "description"}],
		examples=[{"name": "name", "description": "description"}],
	)

	def get_output_fields(self):
		"""
		Retrieves output fields.

		Returns:
			List[str]: A list of output fields.
		"""
		return [field['name'] for field in self.output_template]

class TransformSkill(Skill):
	"""
	Transform skill that transforms a dataframe to another dataframe (e.g. for data annotation purposes).
	See base class Skill for more information about the attributes.
	"""
	def apply(
		self,
		input: InternalDataFrame,
		runtime: Runtime,
	) -> InternalDataFrame:
		"""
		Applies the skill to a dataframe and returns another dataframe.

		Args:
			input (InternalDataFrame): The input data to be processed.
			runtime (Runtime): The runtime instance to be used for processing.

		Returns:
			InternalDataFrame: The transformed data.
		"""

		return runtime.batch_to_batch(
			input,
			input_template=self.input_template,
			output_template=self.output_template,
			instruction_template=self.instruction_template,
		)

class SynthesisSkill(Skill):
	"""
	Synthesis skill that synthesize a dataframe from a record (e.g. for dataset generation purposes).
	See base class Skill for more information about the attributes.
	"""

	def apply(
		self,
		input: Union[Dict, InternalSeries],
		runtime: Runtime,
	) -> InternalDataFrame:
		"""
		Applies the skill to a record and returns a dataframe.

		Args:
			input (InternalSeries): The input data to be processed.
			runtime (Runtime): The runtime instance to be used for processing.

		Returns:
			InternalDataFrame: The synthesized data.
		"""
		if isinstance(input, InternalSeries):
				input = input.to_dict()
		return runtime.record_to_batch(
			input,
			input_template=self.input_template,
			output_template=self.output_template,
			instruction_template=self.instruction_template,
		)


class AnalysisSkill(Skill):
	"""
	Analysis skill that analyzes a dataframe and returns a record (e.g. for data analysis purposes).
	See base class Skill for more information about the attributes.
	"""

	def apply(
		self,
		input: Union[InternalDataFrame, InternalSeries, Dict],
		runtime: Runtime,
	) -> InternalSeries:
		"""
		Applies the skill to a dataframe and returns a record.

		Args:
			input (InternalDataFrame): The input data to be processed.
			runtime (Runtime): The runtime instance to be used for processing.

		Returns:
			InternalSeries: The record containing the analysis results.
		"""
		if isinstance(input, InternalSeries):
				input = input.to_frame()
		elif isinstance(input, dict):
				input = InternalDataFrame([input])

		aggregated_input = input.apply(
			lambda row: self.input_template.format(**row), axis=1
		).str.cat(sep='\n')

		output = runtime.record_to_record(
				{'aggregated_input': aggregated_input},
				input_template='{aggregated_input}',
				output_template=self.output_template,
				instruction_template=self.instruction_template,
		)
		return InternalSeries(output)

class RetrievalSkill(Skill):
	"""
	retrieval skill that process the dataframe and retrieve data from external 
	sources (e.g. for data retrieval purposes).
	"""
	input_template: str
	vector_store: AllyVectorStore
	query_input_fields: List[str]
	query_output_field: str

	def apply(
		self,
		input: InternalDataFrame,
		runtime: Runtime,
	) -> InternalDataFrame:

		input = self.vector_store.batch_to_batch(
			input,
			input_fields=self.query_input_fields,
			output_field=self.query_output_field,
		)
		print_dataframe(input)
		return runtime.batch_to_batch(
			input,
			input_template=self.input_template,
			output_template=self.output_template,
			instruction_template=self.instruction_template,
		)
