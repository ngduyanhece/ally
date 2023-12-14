from typing import Callable, Dict, List

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools.base import BaseTool
from langchain_core.language_models import BaseLanguageModel

from ally.tools.foodally.toolkit import FoodallyNLToolkit, FoodallyToolkit
from ally.tools.foodally.utils import get_foodally_client


def load_tool_kit(
	tool_kit_name: str,
) -> List[BaseTool]:
	"""load the tool from tool_kit by tool_kit_name"""
	return __TOOL_KITS[tool_kit_name].get_tools()

def _get_foodally_toolkit() -> BaseToolkit:
	supabase_client = get_foodally_client()
	return FoodallyToolkit(db=supabase_client)

def _get_foodally_nl_toolkit() -> BaseToolkit:
  	return FoodallyNLToolkit()

__TOOL_KITS: Dict[str, Callable[[BaseLanguageModel], BaseTool]] = {
	"foodally-toolkit": _get_foodally_toolkit(),
	"foodally-nl-toolkit": _get_foodally_nl_toolkit(),
}
