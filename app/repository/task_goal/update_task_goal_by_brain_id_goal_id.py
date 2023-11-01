from uuid import UUID

from app.models.settings import get_supabase_db
from app.models.task_goal import TaskGoalEntity


def update_task_goal_by_brain_id_goal_id(
		brain_id: UUID, goal_id: UUID, task_goal: TaskGoalEntity) -> TaskGoalEntity:
	supabase_db = get_supabase_db()
	response = supabase_db.update_task_goal_by_brain_id_goal_id(
		brain_id=brain_id, goal_id=goal_id, task_goal=task_goal)
	return response