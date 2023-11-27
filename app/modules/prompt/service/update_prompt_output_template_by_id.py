
from uuid import UUID

from app.models.databases.supabase.prompts import \
    PromptOutputTemplateProperties
from app.models.prompt import PromptOutputTemplate
from app.models.settings import get_supabase_db


def update_prompt_output_template_by_id(
	prompt_output_template_id: UUID,
	prompt_output_template: PromptOutputTemplateProperties,
) -> PromptOutputTemplate | None:
	supabase_db = get_supabase_db()
	response = supabase_db.update_prompt_output_template_by_id(
		prompt_output_template_id=prompt_output_template_id,
		prompt_output_template=prompt_output_template
	)
	if response is None:
		return None
	return response
