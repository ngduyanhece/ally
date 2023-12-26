from typing import Optional

from pydantic import BaseModel

from ally.modules.knowledge.entity.knowledge import KnowledgeStatus


class CreateKnowledgeProperties(BaseModel):
	agent_id: str
	file_name: Optional[str] = None
	url: Optional[str] = None
	extension: str = "txt"
	status: KnowledgeStatus = KnowledgeStatus.Pending
	message: Optional[str] = None

	def dict(self, *args, **kwargs):
		knowledge_dict = super().model_dump(*args, **kwargs)
		knowledge_dict["agent_id"] = str(knowledge_dict.get("agent_id"))
		return knowledge_dict
