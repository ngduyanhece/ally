

from abc import ABC, abstractmethod
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
	frozen: bool = Field(
		default=False,
		title="Frozen",
		description="Flag indicating if the skill is frozen.",
		examples=[True, False],
	)

	def get_output_fields(self):
		"""
		Retrieves output fields.

		Returns:
			List[str]: A list of output fields.
		"""
		return [field['name'] for field in self.output_template]
	
	@abstractmethod
	def improve(self, predictions, train_skill_output, feedback, runtime):
		"""
		Base method for improving the skill.
		"""

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
	
	def improve(
		self,
		predictions: InternalDataFrame,
		train_skill_output: str,
		feedback,
		runtime: Runtime,
	):
		"""
		Improves the skill.

		Args:
			predictions (InternalDataFrame): The predictions made by the skill.
			train_skill_output (str): The name of the output field of the skill.
			feedback (InternalDataFrame): The feedback provided by the user.
			runtime (Runtime):

		"""
		output_template_str = " ".join([field['description'] + ": " "{" + field['name'] + "}" for field in self.output_template])
		if (
			feedback.match[train_skill_output].all()
			and not feedback.match[train_skill_output].isna().all()
		):
			# nothing to improve
			return

		fb = feedback.feedback.rename(
			columns=lambda x: x + "__fb" if x in predictions.columns else x
		)
		analyzed_df = fb.merge(predictions, left_index=True, right_index=True)

		examples = []

		for i, row in enumerate(analyzed_df.to_dict(orient="records")):
			# if fb marked as NaN, skip
			if not row[f"{train_skill_output}__fb"]:
				continue
			examples.append(
				f"### Example #{i}\n\n"
				f"{self.input_template.format(**row)}\n\n"
				f"{output_template_str.format(**row)}\n\n"
				f'User feedback: {row[f"{train_skill_output}__fb"]}\n\n'
			)

		examples = "\n".join(examples)

		teacher_instruction_template = """
		You are a helpful assistant
		"""
		# full template
		full_template = f"""
		{{prompt}}
		{self.input_template}
		{output_template_str}"""

		message = f"""
			A prompt is a text paragraph that outlines the expected actions and instructs the large language model (LLM) to \
			generate a specific output. This prompt is concatenated with the input text, and the \
			model then creates the required output.
			This describes the full template how the prompt is concatenated with the input to produce the output:
			```
			{full_template}
			```
			Here:
			- "{self.input_template}" is input template,
			- "{{prompt}}" is the LLM prompt,
			- "{output_template_str}" is the output template.

			Model can produce erroneous output if a prompt is not well defined. \
			In our collaboration, we’ll work together to refine a prompt. The process consists of two main steps:

			## Step 1
			I will provide you with the current prompt along with prediction examples. Each example contains the input text, the final prediction produced by the model, and the user feedback. \
			User feedback indicates whether the model prediction is correct or not. \
			Your task is to analyze the examples and user feedback, determining whether the \
			existing instruction is describing the task reflected by these examples precisely, and suggests changes to the prompt to address the incorrect predictions.

			## Step 2
			Next, you will carefully review your reasoning in step 1, integrate the insights to refine the prompt, \
			and provide me with the new prompt that improves the model’s performance.
			## Current prompt
			{self.instruction_template}
			## Examples
			{examples}
			Summarize your analysis about incorrect predictions and suggest changes to the prompt."""
		
		reasoning = runtime.record_to_record(
			record={'input': message},
			instruction_template=teacher_instruction_template,
			input_template="{input}",
			output_template=[{
				"name": "reasoning",
				"description": "reasoning from the assistant"
			}]
		)['reasoning']

		teacher_instruction_template = f"""
		{reasoning}
		"""

		message = f"""
			Now please carefully review your reasoning in Step 1 and help with Step 2: refining the prompt.
			## Current prompt
			{self.instruction_template}

			## Follow this guidance to refine the prompt:

			1. The new prompt should should describe the task precisely, and address the points raised in the user feedback.

			2. The new prompt should be similar to the current instruction, and only differ in the parts that address the issues you identified in Step 1.
					Example:
					- Current prompt: "The model should generate a summary of the input text."
					- New prompt: "The model should generate a summary of the input text. Pay attention to the original style."

			3. Reply only with the new prompt. Do not include input and output templates in the prompt."""
		new_prompt = runtime.record_to_record(
			record={'input': message},
			instruction_template=teacher_instruction_template,
			input_template="{input}",
			output_template=[{
				"name": "output",
				"description": "new prompt"
			}]
		)['output']
		self.instruction_template = new_prompt
		return new_prompt, reasoning

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
	
	def improve(self, **kwargs):
		"""
		Improves the skill.
		"""
		raise NotImplementedError

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
	
	def improve(self, **kwargs):
		"""
		Improves the skill.
		"""
		raise NotImplementedError
