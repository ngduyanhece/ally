
from uuid import UUID

from app.models.prompt import PromptInputTemplate
from app.models.settings import get_supabase_db


def delete_prompt_input_template_by_id(
	prompt_input_template_id: UUID,
) -> PromptInputTemplate | None:
	supabase_db = get_supabase_db()
	response = supabase_db.delete_prompt_input_template_by_id(
		prompt_input_template_id=prompt_input_template_id,
	)
	if response is None:
		return None
	return response
