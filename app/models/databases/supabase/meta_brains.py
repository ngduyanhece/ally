from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.logger import get_logger
from app.models.brain_entity import MinimalBrainEntity
from app.models.databases.repository import Repository
from app.models.meta_brain_entity import (MetaBrainEntity,
                                          MinimalMetaBrainEntity,
                                          PublicMetaBrain)

logger = get_logger(__name__)
class CreateMetaBrainProperties(BaseModel):
    name: Optional[str] = "Default meta brain"
    description: Optional[str] = "This is a meta brain description"
    status: Optional[str] = "private"
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.0
    max_tokens: Optional[int] = 256
    openai_api_key: Optional[str] = None

    def dict(self, *args, **kwargs):
        meta_brain_dict = super().model_dump(*args, **kwargs)
        return meta_brain_dict

class CreatedMetaBrainOutput(BaseModel):
    meta_brain_id: UUID
    name: str
    rights: str


class MetaBrainUpdatableProperties(BaseModel):
    name: Optional[str]
    description: Optional[str]
    temperature: Optional[float]
    model: Optional[str]
    max_tokens: Optional[int]
    openai_api_key: Optional[str]
    status: Optional[str]
    
    def dict(self, *args, **kwargs):
        metabrain_dict = super().model_dump(*args, **kwargs)
        return metabrain_dict
    
class MetaBrain(Repository):
    def __init__(self, supabase_client):
        self.db = supabase_client

    def create_meta_brain(self, meta_brain: CreateMetaBrainProperties):
        response = (self.db.table("meta_brains").
                    insert(meta_brain.dict())).execute()
        return MetaBrainEntity(**response.data[0])
    
    def get_user_meta_brains(self, user_id) -> list[MinimalMetaBrainEntity]:
        response = (
            self.db.from_("meta_brains_users")
            .select("id:meta_brain_id, rights, meta_brains (meta_brain_id, name, status)")
            .filter("user_id", "eq", user_id)
            .execute()
        )
        user_meta_brains: list[MinimalMetaBrainEntity] = []
        for item in response.data:
            user_meta_brains.append(
                MinimalMetaBrainEntity(
                    id=item["meta_brains"]["meta_brain_id"],
                    name=item["meta_brains"]["name"],
                    rights=item["rights"],
                    status=item["meta_brains"]["status"],
                )
            )
            user_meta_brains[-1].rights = item["rights"]
        return user_meta_brains
    
    def get_public_meta_brains(self) -> list[PublicMetaBrain]:
        response = (
            self.db.from_("meta_brains")
            .select("id:meta_brain_id, name, description, last_update")
            .filter("status", "eq", "public")
            .execute()
        )
        public_meta_brains: list[PublicMetaBrain] = []
        for item in response.data:
            meta_brain = PublicMetaBrain(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                last_update=item["last_update"],
            )
            meta_brain.number_of_subscribers = \
                self.get_meta_brain_subscribers_count(meta_brain.id)
            public_meta_brains.append(meta_brain)
        return public_meta_brains
    
    def get_meta_brain_subscribers_count(self, meta_brain_id: UUID) -> int:
        response = (
            self.db.from_("meta_brains_users")
            .select(
                "count",
            )
            .filter("meta_brain_id", "eq", str(meta_brain_id))
            .execute()).data
        if len(response) == 0:
            raise ValueError(f"Meta Brain with id {meta_brain_id} does not exist.")
        return response[0]["count"]

    def get_default_user_meta_brain_id(self, user_id: UUID) -> UUID | None:
        response = (
            (
                self.db.from_("meta_brains_users")
                .select("meta_brain_id")
                .filter("user_id", "eq", user_id)
                .filter("default_meta_brain", "eq", True)
                .execute()
            )).data
        if len(response) == 0:
            return None
        return UUID(response[0].get("meta_brain_id"))
    
    def get_meta_brain_by_id(self, meta_brain_id: UUID) -> MetaBrainEntity | None:
        response = (
            self.db.from_("meta_brains")
            .select("id:meta_brain_id, name, *")
            .filter("meta_brain_id", "eq", meta_brain_id)
            .execute()
        ).data

        if len(response) == 0:
            return None

        return MetaBrainEntity(**response[0])
    
    def create_meta_brain_user(self, user_id: UUID, meta_brain_id, rights, default_meta_brain: bool):
        response = (
            self.db.table("meta_brains_users")
            .insert(
                {
                    "meta_brain_id": str(meta_brain_id),
                    "user_id": str(user_id),
                    "rights": rights,
                    "default_meta_brain": default_meta_brain,
                }
            )
            .execute()
        )

        return response
    
    def get_meta_brain_for_user(self, user_id, meta_brain_id) -> MinimalMetaBrainEntity | None:
        response = (
            self.db.from_("meta_brains_users")
            .select("id:meta_brain_id, rights, meta_brains (id: meta_brain_id, status, name)")
            .filter("user_id", "eq", user_id)
            .filter("meta_brain_id", "eq", meta_brain_id)
            .execute()
        )
        if len(response.data) == 0:
            return None
        meta_brain_data = response.data[0]

        return MinimalMetaBrainEntity(
            id=meta_brain_data["meta_brains"]["id"],
            name=meta_brain_data["meta_brains"]["name"],
            rights=meta_brain_data["rights"],
            status=meta_brain_data["meta_brains"]["status"],
        )
    
    def delete_meta_brain_user_by_id(
        self,
        user_id: UUID,
        meta_brain_id: UUID,
    ):
        results = (
            self.db.table("meta_brains_users")
            .delete()
            .match({"meta_brain_id": str(meta_brain_id), "user_id": str(user_id)})
            .execute()
        )
        return results.data
    
    def update_meta_brain_by_id(
        self, meta_brain_id: UUID, meta_brain: MetaBrainUpdatableProperties
    ) -> MetaBrainEntity | None:
        update_meta_brain_response = (
            self.db.table("meta_brains")
            .update(meta_brain.dict(exclude_unset=True))
            .match({"meta_brain_id": meta_brain_id})
            .execute()
        ).data

        if len(update_meta_brain_response) == 0:
            return None

        return MetaBrainEntity(**update_meta_brain_response[0])
    
    def update_meta_brain_last_update_time(self, meta_brain_id: UUID) -> None:
        self.db.table("meta_brains").update({"last_update": "now()"}). \
            match({"meta_brain_id": meta_brain_id}).execute()
        
    def get_meta_brain_brains(self, meta_brain_id: UUID, user_id: UUID) -> None:
        response = (
            self.db.from_("brains_meta_brains")
            .select("id:brain_id")
            .filter("meta_brain_id", "eq", meta_brain_id)
            .execute()
        )
        brain_ids = [item["id"] for item in response.data] 
        response = (
            self.db.from_("brains_users")
            .select("id:brain_id, rights, brains (brain_id, name, status)")
            .filter("user_id", "eq", user_id)
            .in_("brain_id", brain_ids)
            .execute()
        )
        user_brains: list[MinimalBrainEntity] = []
        for item in response.data:
            user_brains.append(
                MinimalBrainEntity(
                    id=item["brains"]["brain_id"],
                    name=item["brains"]["name"],
                    rights=item["rights"],
                    status=item["brains"]["status"],
                )
            )
            user_brains[-1].rights = item["rights"]
        return user_brains
        
        

