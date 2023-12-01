
from typing import List
from uuid import UUID

from app.models.prompt import PromptInputTemplate
from app.models.settings import get_supabase_db


def get_all_prompt_input_template_by_prompt_id(
	prompt_id: UUID,
) -> List[PromptInputTemplate]:
	supabase_db = get_supabase_db()
	return supabase_db.get_all_prompt_input_template_by_prompt_id(
		prompt_id=prompt_id,
	)
