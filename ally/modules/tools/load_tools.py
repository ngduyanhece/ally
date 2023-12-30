from typing import Dict

from ally.modules.tools.pre_build.agent_management.create_agent import (
    create_new_agent_tool, create_new_agent_tool_interface)
from ally.modules.tools.pre_build.agent_management.get_all_agents import (
    get_all_agents_tool, get_all_agents_tool_interface)
from ally.modules.tools.pre_build.dummy.dummy import (
    get_current_weather_interface, get_current_weather_tool)

_TOOL_NAME_MAP: Dict[str, object] = {
	"create_new_agent_tool": create_new_agent_tool,
	"get_all_agents_tool": get_all_agents_tool,
	"get_current_weather_tool": get_current_weather_tool
}

_TOOL_INTERFACE_MAP: Dict[str, dict] = {
	"create_new_agent_tool": create_new_agent_tool_interface,
	"get_current_weather_tool": get_current_weather_interface,
	"get_all_agents_tool": get_all_agents_tool_interface
}
