
from uuid import UUID

from app.models.databases.supabase.prompts import PromptInputTemplateProperties
from app.models.prompt import PromptInputTemplate
from app.models.settings import get_supabase_db


def create_prompt_input_template_by_prompt_id(
	prompt_id: UUID,
	prompt_input_template: PromptInputTemplateProperties,
) -> PromptInputTemplate:
	supabase_db = get_supabase_db()
	return supabase_db.create_prompt_input_template_by_prompt_id(
		prompt_id=prompt_id,
		prompt_input_template=prompt_input_template
	)
