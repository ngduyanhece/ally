
from uuid import UUID

from app.models.databases.supabase.prompts import PromptInputTemplateProperties
from app.models.prompt import PromptInputTemplate
from app.models.settings import get_supabase_db


def update_prompt_input_template_by_id(
	prompt_input_template_id: UUID,
	prompt_input_template: PromptInputTemplateProperties,
) -> PromptInputTemplate | None:
	supabase_db = get_supabase_db()
	response = supabase_db.update_prompt_input_template_by_id(
		prompt_input_template_id=prompt_input_template_id,
		prompt_input_template=prompt_input_template
	)
	if response is None:
		return None
	return response
