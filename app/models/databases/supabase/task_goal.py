
from typing import List
from uuid import UUID

from app.models.databases.repository import Repository
from app.models.task_goal import TaskGoalEntity


class TaskGoal(Repository):
		def __init__(self, supabase_client):
				self.db = supabase_client

		def get_task_goals_by_brain_id(self, brain_id: UUID) -> List[TaskGoalEntity]:
			response = (
				self.db.from_("task_goals")
				.select("*")
				.filter("brain_id", "eq", brain_id)
				.execute()
			)
			task_goals: list[TaskGoalEntity] = []
			for task_goal in response.data:
				task_goals.append(TaskGoalEntity(
					goal_id=task_goal["goal_id"],
					title=task_goal["title"],
					content=task_goal["content"],
					goal_achieved=task_goal["goal_achieved"],
				))
			return task_goals
		
		def get_task_goal_by_brain_id_goal_id(self, brain_id: UUID, goal_id: UUID) -> TaskGoalEntity:
			response = (
				self.db.from_("task_goals")
				.select("*")
				.filter("brain_id", "eq", brain_id)
				.filter("goal_id", "eq", goal_id)
				.execute()
			)
			return TaskGoalEntity(**response.data[0])
		
		def update_task_goal_by_brain_id_goal_id(self, brain_id: UUID, goal_id: UUID, task_goal: TaskGoalEntity) -> TaskGoalEntity:
			response = (
				self.db.from_("task_goals")
				.update(task_goal.model_dump())
				.filter("brain_id", "eq", brain_id)
				.filter("goal_id", "eq", goal_id)
				.execute()
			)
			return TaskGoalEntity(**response.data[0])
