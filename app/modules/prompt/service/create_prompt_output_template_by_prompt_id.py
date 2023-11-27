
from uuid import UUID

from app.models.databases.supabase.prompts import \
    PromptOutputTemplateProperties
from app.models.prompt import PromptOutputTemplate
from app.models.settings import get_supabase_db


def create_prompt_output_template_by_prompt_id(
	prompt_id: UUID,
	prompt_output_template: PromptOutputTemplateProperties,
) -> PromptOutputTemplate:
	supabase_db = get_supabase_db()
	return supabase_db.create_prompt_output_template_by_prompt_id(
		prompt_id=prompt_id,
		prompt_output_template=prompt_output_template
	)
