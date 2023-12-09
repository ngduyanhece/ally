
from ally.skills.base import TransformSkill


class QuestionAnsweringSkill(TransformSkill):
	"""
	Skill specialized for answering questions based on the provided input.

	Inherits from the TextGenerationSkill and focuses on generating answers to the questions 
	posed in the input. The class customizes the instructions, input, and output templates 
	specifically for question-answering tasks.

	Attributes:
		instruction_template (str): Instruction to guide the LLM in answering the question.
		input_template (str): Format in which the question is presented to the LLM.
		output_template (str): Expected format of the LLM's answer.
		prediction_field (str): Field name for the generated answer.
	"""
	
	name: str = 'classification'
	description: str = 'tool used to answer questions based on the provided input'
	input_template: str = "Input: {input}"
	instruction_template: str = 'Answer the following question'
	prefix: str = "try to answer the question as best as you can"
