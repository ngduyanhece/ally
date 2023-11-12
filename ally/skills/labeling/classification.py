
from typing import List

from ally.skills.base import LLMSkill


class ClassificationSkill(LLMSkill):
	"""
	Skill specialized for classifying text inputs based on a predefined set of labels.

	Attributes:
		name (str): Unique name of the skill.
		instructions (str): Instructs agent what to do with the input data.
		description (str): Description of the skill.
		input_template (str): Template for the input data.
		output_template (str): Template for the output data.
		input_data_field (str): Name of the input data field.
		prediction_field (str): Name of the prediction field to be used for the output data.
		labels (List[str]): A list of valid labels for the classification task.

	Examples:
		>>> import pandas as pd
		>>> skill = ClassificationSkill(labels=['positive', 'negative'])
		>>> skill.apply(pd.DataFrame({'text': ['I love this movie!', 'I hate this movie!']}))
		text                    predictions score
		I love this movie!      positive   0.99
		I hate this movie!      negative   0.99
	"""
	instructions: str = 'Label the input text with the following labels: {{labels}}'
	labels: List[str]
	output_template: str = "Output: {{select 'predictions' options=labels logprobs='score'}}"
	prediction_field: str = 'predictions'