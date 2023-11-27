
from app.modules.prompt.entity.prompt import PromptInputTemplateEntity

_template = """
{input_template}
this is context you can use to consider when give out the final answer.
context: {context}
"""

def get_input_template_from_a_prompt_inout_template(
		input_template: PromptInputTemplateEntity):
	return " ".join([t.description + ":" + "{" + t.name + "}" for t in input_template])

def retrieval_input_template_from_a_inout_template(
		input_template: PromptInputTemplateEntity):
	input_template = get_input_template_from_a_prompt_inout_template(
		input_template)
	return _template.format(
		input_template=input_template,
		context="{context}"
	)
