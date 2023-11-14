from typing import Dict, List

from ally.skills.base import LLMSkill


class TextGenerationSkill(LLMSkill):
	"""
	 Skill specialized for generating text based on the provided input.

  This involves tasks where the LLM is expected to produce creative, coherent, and contextually 
  relevant textual content based on the given input.

	Attributes:
		instruction_template (str): Instruction to guide the LLM in answering the question.
		input_template (str): Format in which the question is presented to the LLM.
		output_template (str): Expected format of the LLM's answer.
		prediction_field (str): Field name for the generated answer.
	"""
	
	input_template: str = "input: {input}"

	instruction_template: str = 'Generate text based on the provided input.'
	output_template: List[Dict[str, str]] = [
		{
			"name": "answer",
			"description": "text generated by the model"
		}
	]
	prediction_field: str = 'answer'
