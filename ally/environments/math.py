from collections import defaultdict
from typing import Optional

from ally.environments.base import EnvironmentFeedback, StaticEnvironment
from ally.skills.skillset import SkillSet
from ally.utils.internal_data import InternalDataFrame


class MathValidationEnvironment(StaticEnvironment):

	def get_feedback(
		self,
		skills: SkillSet,
		predictions: InternalDataFrame,
		num_feedbacks: Optional[int] = None,
	) -> EnvironmentFeedback:
		"""
		Math environment will check the final output of the skill set against the ground truth.
		if the final output is correct, the environment will mark all the skills as correct.
		if the final output is incorrect, the environment will mark all the skills as incorrect.
		Args:
			skills (SkillSet): The set of skills/models whose predictions are being evaluated.
			predictions (InternalDataFrame): The predictions to compare with the ground truth.
			num_feedbacks (Optional[int], optional): The number of feedbacks to request. Defaults to all predictions
		Returns:
			EnvironmentFeedback: The resulting ground truth signal, with matches and errors detailed.
		"""
		if num_feedbacks is not None:
			predictions = predictions.sample(n=num_feedbacks)
		feedback = defaultdict(list)
		match = defaultdict(list)

		pred_column = list(skills.get_skill_outputs())[-1]
		gt_column = self.ground_truth_columns[pred_column]

		for skill_output, skill_name in skills.get_skill_outputs():
			for _, prediction in predictions.iterrows():
				if prediction[pred_column] == prediction[gt_column]:
					match[skill_output].append(True)
					feedback[skill_output].append("the answer is correct")
				else:
					match[skill_output].append(False)
					feedback[skill_output].append("the answer is incorrect")
		
		return EnvironmentFeedback(
			match=InternalDataFrame(match, index=predictions.index),
			feedback=InternalDataFrame(feedback, index=predictions.index)
		)