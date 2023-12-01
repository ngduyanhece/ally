from typing import Dict, List

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
	
	input_template: str = "Question: {input}"

	instruction_template: str = 'Answer the question.'
	output_template: List[Dict[str, str]] = [
		{
			"name": "answer",
			"description": "the answer to the question"
		}
	]
