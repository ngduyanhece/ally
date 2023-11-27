
from uuid import UUID

from app.models.prompt import PromptOutputTemplate
from app.models.settings import get_supabase_db


def get_prompt_output_template_by_id(
	prompt_output_template_id: UUID,
) -> PromptOutputTemplate:
	supabase_db = get_supabase_db()
	return supabase_db.get_prompt_output_template_by_id(
		prompt_output_template_id=prompt_output_template_id,
	)
