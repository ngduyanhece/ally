
from uuid import UUID

from app.models.prompt import PromptInputTemplate
from app.models.settings import get_supabase_db


def get_prompt_input_template_by_id(
	prompt_input_template_id: UUID,
) -> PromptInputTemplate:
	supabase_db = get_supabase_db()
	return supabase_db.get_prompt_input_template_by_id(
		prompt_input_template_id=prompt_input_template_id,
	)
