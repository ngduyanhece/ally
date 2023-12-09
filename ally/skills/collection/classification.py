

from ally.skills.base import TransformSkill


class ClassificationSkill(TransformSkill):
	"""
	Skill specialized for classifying text inputs based on a predefined set of labels.

	Attributes:
		name (str): Unique name of the skill.
		instruction_template (str): Instructs agent what to do with the input data.
		description (str): Description of the skill.
		input_template (str): Template for the input data.
		output_template: format of the output data
		prediction_field (str): Name of the prediction field to be used for the output data.

	Examples:
		>>> import pandas as pd
		>>> skill = ClassificationSkill(labels=['positive', 'negative'])
		>>> skill.apply(pd.DataFrame({'text': ['I love this movie!', 'I hate this movie!']}))
		text                    predictions score
		I love this movie!      positive   0.99
		I hate this movie!      negative   0.99
	"""
	name: str = 'classification'
	description: str = 'tool used to classify input based on a predefined set of labels'
	input_template: str = "Input: {input}"
	instruction_template: str = 'Label the input text with the following labels'