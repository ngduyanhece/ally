from abc import ABC
from typing import Dict, Optional, Tuple

from pydantic import BaseModel, Field, field_validator

from ally.environments.base import (Environment, EnvironmentFeedback,
                                    StaticEnvironment)
from ally.memories.base import Memory
from ally.runtimes.base import Runtime
from ally.skills.base import Skill
from ally.skills.skillset import LinearSkillSet, SkillSet
from ally.utils.internal_data import InternalDataFrame
from ally.utils.logs import print_dataframe, print_text


class Agent(BaseModel, ABC):
	"""
	Represents a customizable agent that can interact with environments, 
	employ skills, and leverage memory and runtimes.

	Attributes:
	environment (Union[Dataset, Environment]): The environment with which the agent interacts.
	skills (Union[SkillSet, BaseSkill, List[BaseSkill], Dict[str, BaseSkill]]): The skills possessed by the agent.
	memory (LongTermMemory, optional): The agent's long-term memory. Defaults to None.
	runtimes (Dict[str, Runtime], optional): The runtimes available to the agent. Defaults to predefined runtimes.
	default_runtime (str): The default runtime used by the agent. Defaults to 'openai'.
	teacher_runtimes (Dict[str, Runtime], optional): The runtimes available to the agent's teacher. Defaults to predefined runtimes.
	default_teacher_runtime (str): The default runtime used by the agent's teacher. Defaults to 'openai-gpt3'.
	"""
	environment: Environment = None
	skills: SkillSet

	memory: Memory = Field(default=None)
	runtimes: Optional[Dict[str, Runtime]]
	teacher_runtimes: Optional[Dict[str, Runtime]] = None
	default_runtime: str = 'openai'
	default_teacher_runtime: str = 'openai'

	class Config:
		arbitrary_types_allowed = True
	
	def __rich__(self) -> str:
		"""
		Returns a colorized and formatted representation of the Agent instance.

		Returns:
			str: A rich-formatted representation of the agent.
		"""
		
		skill_names = ", ".join([skill.name for skill in self.skills.skills.values()])
		runtime_names = ", ".join(self.runtimes.keys())
		
		return (
			f"[bold blue]Agent Instance[/bold blue]\n\n"
			f"Environment: {self.environment.__class__.__name__}\n"
			f"Skills: {skill_names}\n"
			f"Runtimes: {runtime_names}\n"
			f"Default Runtime: {self.default_runtime}\n"
			f"Default Teacher Runtime: {self.default_teacher_runtime}"
		)
	
	@field_validator('environment', mode='before')
	def environment_validator(cls, v) -> Environment:
		"""
		Validates and possibly transforms the environment attribute:
		if the environment is an InternalDataFrame, it is transformed into a StaticEnvironment.
		"""
		if isinstance(v, InternalDataFrame):
			v = StaticEnvironment(df=v)
		return v
	
	@field_validator('skills', mode='before')
	def skills_validator(cls, v) -> SkillSet:
		"""
		Validates and possibly transforms the skills attribute.
		"""
		if isinstance(v, SkillSet):
			return v
		elif isinstance(v, Skill):
			return LinearSkillSet(skills=[v])
		else:
			raise ValueError(f"skills must be of type SkillSet or Skill, not {type(v)}")
	
	# @model_validator(mode='after')
	# def verify_input_parameters(self):
	# 	"""
	# 	Verifies that the input parameters are valid."""

	# 	def _raise_default_runtime_error(val, runtime, runtimes, default_value):
	# 		print_error(f"The Agent.{runtime} is set to {val}, "
	# 			f"but this runtime is not available in the list: {list(runtimes)}. "
	# 			f"Please choose one of the available runtimes and initialize the agent again, for example:\n\n"
	# 			f"agent = Agent(..., {runtime}='{default_value}')\n\n"
	# 			f"Make sure the default runtime is available in the list of runtimes. For example:\n\n"
	# 			f"agent = Agent(..., runtimes={{'{default_value}': OpenAIRuntime(model='gpt-4')}})\n\n")
	# 		raise ValueError(f"default runtime {val} not found in provided runtimes.")

	# 	if self.default_runtime not in self.runtimes:
	# 		_raise_default_runtime_error(self.default_runtime, 'default_runtime', self.runtimes, 'openai')
		# if self.default_teacher_runtime not in self.teacher_runtimes:
		# 	_raise_default_runtime_error(self.default_teacher_runtime, 'default_teacher_runtime', self.teacher_runtimes,
		# 																	'openai-gpt4')
		# return self
	
	def get_runtime(self, runtime: Optional[str] = None) -> Runtime:
		"""
		Retrieves the specified runtime or the default runtime if none is specified.

		Args:
			runtime (str, optional): The name of the runtime to retrieve. Defaults to None.

		Returns:
			Runtime: The requested runtime.

		Raises:
			ValueError: If the specified runtime is not found.
		"""
				
		if runtime is None:
			runtime = self.default_runtime
		if runtime not in self.runtimes:
			raise ValueError(f'Runtime "{runtime}" not found.')
		return self.runtimes[runtime]

	def get_teacher_runtime(self, runtime: Optional[str] = None) -> Runtime:
		"""
		Retrieves the specified teacher runtime or the default runtime if none is specified.

		Args:
			runtime (str, optional): The name of the runtime to retrieve. Defaults to None.

		Returns:
			Runtime: The requested runtime.

		Raises:
			ValueError: If the specified runtime is not found.
		"""

		if runtime is None:
			runtime = self.default_teacher_runtime
		if runtime not in self.teacher_runtimes:
			raise ValueError(f'Teacher Runtime "{runtime}" not found.')
		return self.teacher_runtimes[runtime]

	def run(
		self,
		input: InternalDataFrame = None,
		runtime: Optional[str] = None
	) -> InternalDataFrame:
		"""
		Runs the agent on the specified dataset.

		Args:
			dataset (Union[Dataset, InternalDataFrame]): The dataset to run the agent on.
			runtime (str, optional): The name of the runtime to use. Defaults to None, use the default runtime.

		Returns:
			InternalDataFrame: The dataset with the agent's predictions.
		"""
		if input is None:
			input = self.environment.get_data_batch()
		runtime = self.get_runtime(runtime=runtime)
		predictions = self.skills.apply(input, runtime=runtime)
		return predictions

	def select_skill_to_train(
		self, 
		feedback: EnvironmentFeedback,
		accuracy_threshold: float
	) -> Tuple[str, str, float]:
		"""
		Selects the skill to train based on the feedback signal.

		Args:
			feedback (Feedback): The feedback signal.
			accuracy_threshold (float): The accuracy threshold to use for selecting the skill to train.

		Returns:
			str: The name of the skill to train.
			str: The name of the skill output to train.
			float: The accuracy score of the skill to train.
		"""

		# Use ground truth signal to find the skill to improve
		# TODO: what if it is not possible to estimate accuracy per skill?
		accuracy = feedback.get_accuracy()
		train_skill_name, train_skill_output, acc_score = '', '', None
		for skill_output, skill_name in self.skills.get_skill_outputs().items():
			if accuracy[skill_output] < accuracy_threshold:
				train_skill_name, train_skill_output = skill_name, skill_output
				acc_score = accuracy[skill_output]
				break

		return train_skill_name, train_skill_output, acc_score
	
	def pe_optimization(self, skill, examples, teacher_runtime):
		teacher_instruction_template = """
		You are a helpful assistant
		"""
		message = f"""
		A prompt is a text paragraph that outlines the expected actions and instructs the model to \
		generate a specific output. This prompt is concatenated with the input text, and the \
		model then creates the required output. Formally, the prompt is a prefix to the input:
		output = model(concatenate(prompt, input))
		Model can produce erroneous output if the prompt is not well defined. \
		In our collaboration, we’ll work together to refine a prompt. The process consists of two main steps:

		## Step 1
		I will provide you with the current prompt, how the prompt is concatenated with the input text
		(i.e., "full template"), along with some example(s) that are associated with
		this prompt. Each example contains the input, the final answer produced by the model, and the user feedback.
		Your task is to analyze the examples, determining whether the
		existing prompt is decsribing the task reflected by these examples precisely, and suggest
		changes to the prompt.

		## Step 2
		Next, you will carefully review your reasoning in step 1, integrate the insights to craft a
		new, optimized prompt.
		## Current Prompt
		{skill.instruction_template}

		## Full Template
		{{current prompt}}
		{skill.input_template}
		{skill.output_template}
		## Examples
		{examples}
		## Instructions
		For some of these examples, the user feedback points out that the model is not producing the correct output. \
		This may be due to the prompt being misleading or not describing the task precisely. 

		Please examine the example(s) carefully. Note that the user feedback should be considered as ground truth, but \
		the prompts (task descriptions) may be incorrect and need modification.
		For each example, provide reasoning according to the following template:

		### Example <id>
		Input: <input>
		Output: <output>
		Feedback: <feedback>
		Is the output correct according to the feedback: <yes or no, and your reasoning>
		To output the correct label, is it necessary to edit the prompt: <yes or no, and your
		reasoning>
		If yes, provide detailed analysis and actionable suggestions to edit the prompt: <analysis and
		suggestions>
		If yes, and you think there is some knowledge to learn to answer this example, please
		provide the knowledge: <knowledge>
		"""
		reasoning = teacher_runtime.record_to_record(
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
		{skill.instruction_template}
		
		## Instructions
		- The new prompt should be concise and direct.
		- The new prompt should should describe the task precisely and address the points raised in the user feedback.
		- Include a few examples in the prompt to help the model learn the task, by providing inputs and outputs that follow full template.
		- Reply only with the prompt. Do not include other text.
		"""
		new_prompt = teacher_runtime.record_to_record(
				record={'input': message},
				instruction_template=teacher_instruction_template,
				input_template="{input}",
				output_template=[{
					"name": "output",
					"description": "new prompt"
				}]
			)['output']
		return new_prompt, reasoning
  		
	def learn(
		self,
		learning_iterations: int = 3,
		accuracy_threshold: float = 0.9,
		update_memory: bool = True,
		batch_size: Optional[int] = None,
		num_feedbacks: Optional[int] = None,
		runtime: Optional[str] = None,
		teacher_runtime: Optional[str] = None,
	):
		"""
		Enables the agent to learn and improve its skills based on interactions with its environment.

		Args:
			learning_iterations (int, optional): The number of iterations for learning. Defaults to 3.
			accuracy_threshold (float, optional): The desired accuracy threshold to reach. Defaults to 0.9.
			update_memory (bool, optional): Flag to determine if memory should be updated after learning. Defaults to True.
			num_feedbacks (int, optional): The number of predictions to request feedback for. Defaults to None.
			runtime (str, optional): The runtime to be used for the learning process. Defaults to None.
			teacher_runtime (str, optional): The teacher runtime to be used for the learning process. Defaults to None.
		"""

		runtime: Runtime = self.get_runtime(runtime=runtime)
		teacher_runtime: Runtime = self.get_teacher_runtime(runtime=teacher_runtime)

		experience = ""
		final_instruction = ""
		for iteration in range(learning_iterations):

			print_text(f'\n\n=> Iteration #{iteration}: Getting feedback, analyzing and improving ...')

			inputs = self.environment.get_data_batch(batch_size)

			predictions = self.skills.apply(inputs, runtime=runtime)

			feedback = self.environment.get_feedback(self.skills, predictions, num_feedbacks=num_feedbacks)
			print('Predictions and feedback:')
			fb = feedback.feedback.rename(columns=lambda x: x + '__fb' if x in predictions.columns else x)
			analyzed_df = fb.merge(predictions, left_index=True, right_index=True)
			print_dataframe(analyzed_df)

			train_skill_name, train_skill_output, accuracy = self.select_skill_to_train(feedback, accuracy_threshold)
			if not train_skill_name:
				print_text('No skill to improve found. Continue learning...')
				continue

			train_skill = self.skills[train_skill_name]
			print_text(f'Output to improve: "{train_skill_output}" (Skill="{train_skill_name}")\n'
                       f'Accuracy = {accuracy * 100:0.2f}%', style='bold red')
			
			examples = []
			for row in analyzed_df.to_dict(orient='records'):
				# if fb marked as NaN, skip
				if not row[f'{train_skill_output}__fb']:
					continue
				output_template_str = " ".join([t["description"] + ":" + "{" + t["name"] + "}" for t in train_skill.output_template])
				examples.append(
						f'{train_skill.input_template.format(**row)}\n'
						f'{output_template_str.format(**row)}\n'
						f'Feedback: {row[f"{train_skill_output}__fb"]}\n\n'
				)
			new_instructions, reasoning = self.pe_optimization(train_skill, '\n'.join(examples), teacher_runtime)
			experience += f"\n{reasoning}\n"
			train_skill.instruction_template = new_instructions
			final_instruction = new_instructions
			print_text(f'{train_skill.instruction_template}', style='bold green')

		#return the best prompt and the accumulated experience
		return final_instruction, experience