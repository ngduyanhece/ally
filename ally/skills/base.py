

from abc import ABC, abstractmethod
from typing import List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field

from ally.datasets.base import Dataset
from ally.datasets.dataframe import DataFrameDataset
from ally.memories.base import Memory
from ally.runtimes.base import LLMRuntime, Runtime
from ally.utils.internal_data import InternalDataFrame, InternalDataFrameConcat


class BaseSkill(BaseModel, ABC):
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
	prediction_field: Optional[str] = Field(
		title='Prediction field',
		description='Prediction field name that will be used to match ground truth labels.'
								'Should match at least one output field in `output_template`, e.g. \'predictions\'',
		examples=['predictions'],
		default='predictions'
	)

	def __call__(
		self,
		input: InternalDataFrame,
		runtime: LLMRuntime,
		dataset: Dataset
	) -> InternalDataFrame:
		"""Calls the runtime to process a batch of inputs. Input and
		output shapes can be varying, and it should also take care of
		data types validation

		Args:
			input (InternalDataFrame): Input data in the form of an InternalDataFrame.
			runtime (Runtime): The runtime instance to be used for processing.
			dataset (Dataset): The dataset containing the data to be processed.
		
		Returns:
			InternalDataFrame: Concatenated dataframe with the original input and the predictions from the runtime.

		"""

		# get user defined dataset input fields

		runtime_predictions = runtime.process_batch(
			batch=input,
			input_template=self.input_template,
			output_template=self.output_template,
			instruction_template=self.instruction_template,
		)
		runtime_predictions.rename(
			columns={self.prediction_field: self.name}, inplace=True)
		output = input.copy()
		output[runtime_predictions.columns] = \
			runtime_predictions[runtime_predictions.columns]
		return output
	
	@abstractmethod
	def apply(
			self, dataset: Dataset,
			runtime: Runtime,
	) -> InternalDataFrame:
		"""
		Applies the skill to a dataset and returns the results.
		
		Args:
			dataset (Dataset): The dataset on which the skill is to be applied.
			runtime (Runtime): The runtime instance to be used for processing.

		Returns:
			ShortTermMemory: The updated experience after applying the skill.
		"""        
	
	@abstractmethod
	def analyze(
		self,
		predictions: InternalDataFrame,
		errors: InternalDataFrame,
		student_runtime: Runtime,
		teacher_runtime: Optional[Runtime] = None,
		memory: Optional[Memory] = None,
	) -> str:
		"""
		Analyzes the results to derive new experiences.
		It gets provided skill predictions in the format:

		```markdown
		| input | skill_1 | skill_2 | skill_3 |
		|-------|---------|---------|---------|
		| text1 | label11 | label21 | label31 |
		| text2 | label12 | label22 | label32 |
		| ...   | ...     | ...     | ...     |
		```

		and the errors for a specific skill to analyze in the format:

		```markdown
		| prediction | ground_truth |
		|------------|--------------|
		| label11    | label12      |
		| ...        | ...          |
		```

		and returns the string that contains the error analysis report.
		
		Args:
			predictions (InternalDataFrame): The predictions made by the skill.
			errors (InternalDataFrame): The errors made by the skill.
			student_runtime (Runtime): The runtime instance used to get predictions.
			teacher_runtime (Optional[Runtime]): The runtime instance to be used for analysing the errors.
			memory (Optional[Memory]): The memory instance to be used for processing.

		Returns:
			str: The error analysis report.
		"""
	@abstractmethod
	def improve(
		self,
		error_analysis: str,
		runtime: Runtime
	):
		"""
		Refines the LLM skill based on its recent experiences and updates the skill's instructions.

		Args:
			error_analysis (str): The error analysis report.
			runtime (Runtime): The runtime instance to be used for processing.
		"""

class LLMSkill(BaseSkill):
	"""
	A skill specialized for Language Models (LLM). Inherits from the BaseSkill 
	class and provides specific implementations for handling LLM predictions based 
	on given instructions.

	Attributes:
		name (str): Unique name of the skill.
		instruction_template (str): Instructs agent what to do with the input data.
		description (str): Description of the skill.
		input_template (str): Template for the input data.
		output_template (str): Template for the output data.
		prediction_field (str): Name of the prediction field to be used for the output data.
	"""

	def apply(
		self,
		dataset: Union[Dataset, InternalDataFrame],
		runtime: LLMRuntime,
	) -> InternalDataFrame:
		"""
		Applies the LLM skill on a dataset and returns the results.

		Args:
			dataset (Union[Dataset, InternalDataFrame]): The dataset on which the skill is to be applied.
			runtime (LLMRuntime): The runtime instance to be used for processing.

		Returns:
			predictions (InternalDataFrame): The predictions made by the skill.
		"""

		predictions = []
		if isinstance(dataset, InternalDataFrame):
			dataset = DataFrameDataset(df=dataset)

		for batch in dataset.batch_iterator():
			runtime_predictions = self(batch, runtime, dataset)
			predictions.append(runtime_predictions)

		if predictions:
			return InternalDataFrameConcat(predictions, copy=False)

		return InternalDataFrame(columns=dataset.df.columns.tolist() + [self.name])
	
	def analyze(
		self,
		predictions: InternalDataFrame,
		errors: InternalDataFrame,
		student_runtime: LLMRuntime,
		teacher_runtime: Optional[LLMRuntime] = None,
		memory: Optional[Memory] = None
	) -> str:
		"""
		Analyzes the results to identify any discrepancies and returns the observed experience.
		
		Args:
			predictions (InternalDataFrame): The predictions made by the skill.
			errors (InternalDataFrame): The errors made by the skill.
			student_runtime (Runtime): The runtime instance used to get predictions.
			teacher_runtime (Optional[Runtime]): The runtime instance to be used for analysing the errors.
			memory (Optional[Memory]): The memory instance to be used for processing.

		Returns:
			str: The error analysis report.
		"""

		# collect errors and create error report
		# first sample errors - make it uniform, but more sophisticated sampling can be implemented
		MAX_ERRORS = 3
		errors = errors.sample(n=min(MAX_ERRORS, errors.shape[0]))
		# TODO: ground truth column name can be the input parameter that comes from GT signal
		ground_truth_column_name = errors.columns[-1]

		# get error prepared inputs
		inputs = student_runtime.process_batch(
			batch=predictions.loc[errors.index],
			input_template=self.input_template,
			output_template=[
				{
					"name": "input",
					"description": "the original user input"
				}
			],
			instruction_template="get the original user input for error analysis",
		)
		
		if not teacher_runtime:
			teacher_runtime = student_runtime

		predictions_and_errors = pd.concat([
			inputs,
			predictions[self.name].loc[errors.index],
			errors[ground_truth_column_name]
		], axis=1)
		predictions_and_errors.columns = ['input', 'prediction', 'ground_truth']
		# TODO: move handlebars to Runtime level and abstract template language for skill
		# For example, using f-string format as generic, that translates to handlebars inside GuidanceRuntime
		error_reasons = teacher_runtime.process_batch(
				batch=predictions_and_errors,
				instruction_template=f"""
					LLM prompt was created by concatenating instructions with text input:\n\n
					Prediction = LLM(Input, Instructions)\n\n
					We expect the prediction to be equal to the ground truth.\n
					Your task is to provide a reason for the error due to the original instruction.\n
					Be concise and specific.\n\n
					instruction_template: {self.instruction_template}\n
				""",
				input_template="""
					Input: {input}\n
					Prediction: {prediction}\n"
					Ground truth: {ground_truth}\n
					Error reason:\n
				""",
				output_template=[{
						"name": "reason",
						"description": "Error reason"
				}],
		)
		predictions_and_errors['reason'] = error_reasons['reason']
		# build error report
		result = teacher_runtime.process_batch(
				batch=predictions_and_errors,
				output_template=[
					{
						"name": "result",
						"description": "Error analysis report"
					}
				],
				input_template="""
					Input: {input}\n
					Prediction: {prediction}\n"
					Ground truth: {ground_truth}\n"
					Error reason: {reason}\n
					""",
				instruction_template="""
					build the Error analysis report base on the following:
					1. Input
					2. Prediction
					3. Ground truth
					4. Error reason
				"""
		)
		# no specific output specified, all output is in the error report
		error_report = ' '.join(result['result'])
		return error_report
	
	def improve(
		self,
		error_analysis: str,
		runtime: LLMRuntime,
	):
		"""
		Refines the LLM skill based on its recent experiences and updates the skill's instructions.

		Args:
				error_analysis (str): The error analysis report.
				runtime (Runtime): The runtime instance to be used for processing.
		"""

		result = runtime.process_record(
				record={
						'error_analysis': error_analysis
				},
				instruction_template="""
					LLM prompt was created by concatenating instructions with text input:\n\n
					Prediction = LLM(Input, Instructions)\n\n
					We expect the prediction to be equal to the ground truth.\n
					Your task is to analyze errors made by old instructions 
					and craft new instructions for the LLM.\n
					Follow best practices for LLM prompt engineering.\n
					Include 2-3 examples at the end of your response to demonstrate how the new instruction would be applied.\n
					Use the following format for your examples:\n
					Input: ...\n
					Output: ...\n\n
				""",
				input_template=f"""
					Old instructions: {self.instruction_template}\n\n
					Errors:\{error_analysis}\n"
					New instruction:\n
				""",
				output_template=[{
					"name": "new_instruction",
					"description": "New instruction"
				}],
		)
		self.instruction_template = result['new_instruction']