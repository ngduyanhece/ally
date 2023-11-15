from typing import Dict, List

from ally.skills.base import LLMSkill


class SummarizationSkill(LLMSkill):
	"""
	Skill specialized for summarization based on the provided input.

	Inherits from the LLMSkill and focuses on generating answers to the questions 
	posed in the input. The class customizes the instructions, input, and output templates 
	specifically for question-answering tasks.

	Attributes:
		instruction_template (str): Instruction to guide the LLM in answering the question.
		input_template (str): Format in which the question is presented to the LLM.
		output_template (str): Expected format of the LLM's answer.
		prediction_field (str): Field name for the generated answer.
	"""
	
	input_template: str = "text to summarize: {input}"

	instruction_template: str = 'summarize the text'
	output_template: List[Dict[str, str]] = [
		{
			"name": "summary",
			"description": "the summary of the text"
		}
	]
	prediction_field: str = 'summary'
