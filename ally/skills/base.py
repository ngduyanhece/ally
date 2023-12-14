

from abc import ABC, abstractmethod
from typing import List, Optional

from langchain.agents.load_tools import load_tools
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel

from ally.runtimes.base import Runtime
from ally.tools.load_tools import load_tool_kit
from ally.utils.internal_data import InternalDataFrame
from ally.utils.logs import print_text
from ally.vector_store.base import AllyVectorStore

FORMAT_INSTRUCTIONS = """ You have access to the following tools:
Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
please reply the final answer in vietnamese language
the answer should be contain as much information as possible
"""


class Skill(BaseModel, ABC):
	"""
	A foundational abstract class representing a skill. This class sets the foundation 
	for all skills and provides common attributes and methods for skill-based operations.

	Attributes:
		name (str): Unique name of the skill this will be use for the name of the tool function when constructing agent.
		description (str): Description the default tool.
		input_template (str): Template for the human system input
		instruction_template (str): Instructs agent what to do with the input data.
		tool_names (Optional[List[str]]): List of tool names to use for the skill.
		tool_kit_names (Optional[List[str]]): List of tool kit names to use for the skill.
		tool_kwargs (Optional[dict]): Dictionary of keyword arguments to use when loading the tool.
	"""
	name: str
	description: str = ""
	input_template: str = "Input: {input}"
	instruction_template: str = ""
	prefix: str = """
		Answer the following questions as best you can if you cannot answer the question
		please use the only tool you have access to
	"""
	format_instructions: str = FORMAT_INSTRUCTIONS
	conversation_buffer_memory: Optional[ConversationBufferMemory] = None
	tool_names: Optional[List[str]] = []
	tool_kit_names: Optional[List[str]] = []
	tool_kwargs: Optional[dict] = {}
	
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
		if len(self.tool_names) > 0:
			tools = load_tools(self.tool_names, **self.tool_kwargs)
		else:
			tools = []
		if len(self.tool_kit_names) > 0:
			tools_from_tool_kits = [load_tool_kit(tool_kit_name) for tool_kit_name in self.tool_kit_names]
			tools_from_tool_kits = [tool for tool_list in tools_from_tool_kits for tool in tool_list]
			tools.extend(tools_from_tool_kits)

		return runtime.batch_to_batch(
			batch=input,
			input_template=self.input_template,
			instruction_template=self.instruction_template,
			default_llm_function_name=self.name,
			default_llm_function_description=self.description,
			prefix=self.prefix,
			format_instructions=self.format_instructions,
			conversation_buffer_memory=self.conversation_buffer_memory,
			tools=tools
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
		if (feedback.match[train_skill_output].all() and not feedback.match[
			train_skill_output].isna().all()
		):
			# nothing to improve
			return
		output_template_str = "output: {output}"
		intermediate_steps_str = "intermediate steps: {intermediate_steps}"
		fb = feedback.feedback.rename(
			columns=lambda x: x + "__fb" if x in predictions.columns else x
		)
		analyzed_df = fb.merge(predictions, left_index=True, right_index=True)

		prompt_examples = []

		for i, row in enumerate(analyzed_df.to_dict(orient="records")):
			# if fb marked as NaN, skip
			if not row[f"{train_skill_output}__fb"]:
				continue
			prompt_examples.append(
				f"### Example #{i}\n"
				f"input: {self.input_template.format(**row)}\n"
				f"output: {output_template_str.format(**row)}\n"
				f'User feedback: {row[f"{train_skill_output}__fb"]}\n\n'
			)

		prompt_examples = "\n".join(prompt_examples)

		format_instructions_examples = []

		for i, row in enumerate(analyzed_df.to_dict(orient="records")):
			# if fb marked as NaN, skip
			if not row[f"{train_skill_output}__fb"]:
				continue
			format_instructions_examples.append(
				f"### Example #{i}\n"
				f"input: {self.input_template.format(**row)}\n"
				f"output: {intermediate_steps_str.format(**row)}\n"
				f'User feedback: {row[f"{train_skill_output}__fb"]}\n\n'
			)

		format_instructions_examples = "\n".join(format_instructions_examples)

		teacher_instruction_tool_template = """
		You are a helpful assistant
		"""
		teacher_instruction_agent_prefix = """
		you are an agent designed to suggest the improvement for other agent as best you can.
		your task is
		1. to suggest the changing for prompt of the default LLM tool of agent
		2. to suggest the changing for format instruction of agent
		You have access to the following tools:
		"""
		teacher_format_instructions = """Use the following format:
		Question: the input question you must answer
		Thought: you should always think about what to do
		Action: the action to take, should be one of [{tool_names}]
		Action Input: the input to the action
		Observation: the result of the action
		... (this Thought/Action/Action Input/Observation can repeat N times)
		Thought: I now know the final answer
		Final Answer: the final answer to the original input question
		"""

		message_to_reasoning_for_prompt = f"""
		Agent is an AI model designed to complete a specific task. Agent can access to tools.
		One Agent will have a default tool and the main logic of this tool is prompt.
		A prompt is a text paragraph that outlines the expected actions and instructs the large language model (LLM) to \
		generate a specific output. This prompt is concatenated with the input text, and the \
		model then creates the required output.
		Model can produce erroneous output if a prompt is not well defined. \
		In our collaboration, we’ll work together to refine a prompt for the default tool. The process consists of two main steps:

		## Step 1
		I will provide you with the current prompt along with prediction examples. Each example contains the input text, the prompt, the final prediction produced by the model, and the user feedback. \
		User feedback indicates whether the model prediction is correct or not. \
		Your task is to analyze the examples and user feedback, determining whether the \
		existing instruction is describing the task reflected by these examples precisely, and suggests changes to the prompt to address the incorrect predictions.

		## Step 2
		Next, you will carefully review your reasoning in step 1, integrate the insights to refine the prompt, \
		and provide me with the new prompt that improves the model’s performance.
		## Current prompt
		{self.instruction_template}
		## Examples
		{prompt_examples}
		Summarize your analysis about incorrect predictions and suggest changes to the prompt."""
		
		prompt_reasoning = runtime.record_to_record(
			record={'input': message_to_reasoning_for_prompt},
			input_template="{input}",
			instruction_template=teacher_instruction_tool_template,
			default_llm_function_name="agent_behavior_correction",
			default_llm_function_description="this tool is used to correct agent behavior",
			prefix=teacher_instruction_agent_prefix,
			format_instructions=teacher_format_instructions,
		)['output']

		message_to_improve_prompt = f"""
			Now please carefully review your reasoning in Step 1 and help with Step 2: refining the prompt.
			## Current prompt
			{self.instruction_template}

			## Follow this guidance to refine the prompt:

			1. The new prompt should should describe the task precisely, and address the points raised in the user feedback.

			2. The new prompt should be similar to the current instruction, and only differ in the parts that address the issues you identified in Step 1.
					Example:
					- Current prompt: "The model should generate a summary of the input text."
					- New prompt: "The model should generate a summary of the input text. Pay attention to the original style."

			3. Reply only with the new prompt. Do not include input and output templates in the prompt. remove any special characters from the prompt.
			"""
		new_prompt = runtime.record_to_record(
			record={'input': message_to_improve_prompt},
			input_template="{input}",
			instruction_template=prompt_reasoning,
			default_llm_function_name="agent_behavior_correction",
			default_llm_function_description="this tool is used to correct agent behavior",
			prefix=teacher_instruction_agent_prefix,
			format_instructions=teacher_format_instructions,
		)['output']

		# filter all curly brackets from the new prompt

		new_prompt = new_prompt.replace("{", "").replace("}", "")

		# message_to_improve_the_format_instructions = f"""
		# Agent is an AI model designed to complete a specific task. Agent can access to tools.
		# while solving a specific task, agent will follow the format instruction to plan how to solve the task.
		# In this step agent will select tools to  and sequence of tools to solve the task.
		# In our collaboration, we’ll work together to refine the format instruction for the agent. The process consists of two main steps:
		# ## Step 1
		# I will provide you with the current format instruction along with prediction examples. Each example contains the input text, the intermediate steps, the final prediction produced by the model, and the user feedback. \
		# User feedback indicates whether the model prediction is correct or not. \
		# Your task is to analyze the examples and user feedback, determining whether the \
		# existing format instruction is describing the task reflected by these examples precisely, and suggests changes to the format instruction to address the incorrect predictions.
		# ## Step 2
		# Next, you will carefully review your reasoning in step 1, integrate the insights to refine the prompt, \
		# and provide me with the new format instructions that improves the model’s performance.
		# ## Current format instruction
		# {self.format_instructions}
		# ## Examples
		# {format_instructions_examples}
		# Summarize your analysis about incorrect predictions and suggest changes to the format instructions.
		# """
		# format_instructions_reasoning = runtime.record_to_record(
		# 	record={'input': message_to_improve_the_format_instructions},
		# 	input_template="{input}",
		# 	instruction_template=teacher_instruction_tool_template,
		# 	default_llm_function_name="agent_behavior_correction",
		# 	default_llm_function_description="this tool is used to correct agent behavior",
		# 	prefix=teacher_instruction_agent_prefix,
		# 	format_instructions=teacher_format_instructions,
		# )['output']

		# message_to_improve_format_instructions = f"""
		# Now please carefully review your reasoning in Step 1 and help with Step 2: refining the format instructions
		# ## Current format instructions
		# '''
		# {self.format_instructions}
		# '''

		# ## Follow this guidance to refine the format instructions:

		# 1. The new format instructions should describe how the agent solve the task precisely, and address the points raised in the user feedback.

		# 2. The new format instructions should be similar to the current format instructions, and only differ in the parts that address the issues you identified in Step 1.

		# 3. Please always include {{tool_names}} in the format instructions. The agent will replace {{tool_names}} with the names of the tools it selects to solve the task."""

		# new_format_instructions = runtime.record_to_record(
		# 	record={'input': message_to_improve_format_instructions},
		# 	input_template="{input}",
		# 	instruction_template=format_instructions_reasoning,
		# 	default_llm_function_name="agent_behavior_correction",
		# 	default_llm_function_description="this tool is used to correct agent behavior",
		# 	prefix=teacher_instruction_agent_prefix,
		# 	format_instructions=teacher_format_instructions,
		# )['output']

		self.instruction_template = new_prompt
		# self.format_instructions = new_format_instructions
		print_text(f"New prompt: {self.instruction_template}")
		# print_text(f"New format instructions: {self.format_instructions}")
		print_text(f"prompt reasoning: {prompt_reasoning}")
		# print_text(f"format instruction reasoning: {format_instructions_reasoning}")
	

class RetrievalSkill(TransformSkill):
	"""
	retrieval skill that process the dataframe and retrieve data from external 
	sources (e.g. for data retrieval purposes).
	"""
	input_template: str
	vector_store: AllyVectorStore
	query_input_fields: List[str]
	k: int = 1

	def apply(
		self,
		input: InternalDataFrame,
		runtime: Runtime,
	) -> InternalDataFrame:

		input = self.vector_store.batch_to_batch(
			input,
			input_fields=self.query_input_fields,
			k=self.k,
		)
		if len(self.tool_names) > 0:
			tools = load_tools(self.tool_names, **self.tool_kwargs)
		else:
			tools = []
		if len(self.tool_kit_names) > 0:
			tools_from_tool_kits = [load_tool_kit(tool_kit_name) for tool_kit_name in self.tool_kit_names]
			tools_from_tool_kits = [tool for tool_list in tools_from_tool_kits for tool in tool_list]
			tools.extend(tools_from_tool_kits)

		return runtime.batch_to_batch(
			batch=input,
			input_template=self.input_template,
			instruction_template=self.instruction_template,
			default_llm_function_name=self.name,
			default_llm_function_description=self.description,
			prefix=self.prefix,
			format_instructions=self.format_instructions,
			conversation_buffer_memory=self.conversation_buffer_memory,
			tools=tools
		)
