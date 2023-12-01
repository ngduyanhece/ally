from pydantic import BaseModel


class TaskGoalEntity(BaseModel):
    goal_id: str
    title: str
    content: str
    goal_achieved: bool