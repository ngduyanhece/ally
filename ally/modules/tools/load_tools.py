from typing import Dict

from modules.tools.pre_build.agent_management.create_agent import (
    create_new_agent_tool, create_new_agent_tool_interface)
from modules.tools.pre_build.agent_management.create_agent_memory import (
    create_agent_memory_tool, create_agent_memory_tool_interface)
from modules.tools.pre_build.agent_management.get_all_agents import (
    get_all_agents_tool, get_all_agents_tool_interface)
from modules.tools.pre_build.agent_management.retrieve_agent_memory import (
    retrieve_agent_memory_tool, retrieve_agent_memory_tool_interface)
from modules.tools.pre_build.agent_management.update_agent_memory import (
    update_agent_memory_tool, update_agent_memory_tool_interface)
from modules.tools.pre_build.coingecko.get_detail import (
    get_detail_of_token_from_coingecko_tool,
    get_detail_of_token_from_coingecko_tool_interface)
from modules.tools.pre_build.coingecko.get_list import (
    get_all_of_token_from_coingecko_tool,
    get_all_of_token_from_coingecko_tool_interface)
from modules.tools.pre_build.coingecko.get_market_chart import (
    get_market_chart_of_token_from_coingecko_tool,
    get_market_chart_of_token_from_coingecko_tool_interface)
from modules.tools.pre_build.coingecko.get_trending import (
    get_trending_token_from_coingecko_tool,
    get_trending_token_from_coingecko_tool_interface)
from modules.tools.pre_build.cryptopanic.get_news import (
    get_news_from_cryptopanic_tool, get_news_from_cryptopanic_tool_interface)
from modules.tools.pre_build.dummy.dummy import (get_current_weather_interface,
                                                 get_current_weather_tool)
from modules.tools.pre_build.gemini.ask_gemini import (
    ask_gemini_tool, ask_gemini_tool_interface)
from modules.tools.pre_build.gemini.publish_to_avoca import (
    publish_content_to_avoca_tool, publish_content_to_avoca_tool_interface)

_TOOL_NAME_MAP: Dict[str, object] = {
	"create_new_agent_tool": create_new_agent_tool,
	"get_all_agents_tool": get_all_agents_tool,
	"create_agent_memory_tool": create_agent_memory_tool,
	"update_agent_memory_tool": update_agent_memory_tool,
	"get_current_weather_tool": get_current_weather_tool,
	"get_trending_token_from_coingecko_tool": get_trending_token_from_coingecko_tool,
	"get_detail_of_token_from_coingecko_tool": get_detail_of_token_from_coingecko_tool,
	"get_all_of_token_from_coingecko_tool": get_all_of_token_from_coingecko_tool,
	"get_market_chart_of_token_from_coingecko_tool": get_market_chart_of_token_from_coingecko_tool,
	"get_news_from_cryptopanic_tool": get_news_from_cryptopanic_tool,
	"retrieve_agent_memory_tool": retrieve_agent_memory_tool,
	"ask_gemini_tool": ask_gemini_tool,
	"publish_content_to_avoca_tool": publish_content_to_avoca_tool
}

_TOOL_INTERFACE_MAP: Dict[str, dict] = {
	"create_new_agent_tool": create_new_agent_tool_interface,
	"get_current_weather_tool": get_current_weather_interface,
	"get_all_agents_tool": get_all_agents_tool_interface,
	"create_agent_memory_tool": create_agent_memory_tool_interface,
	"update_agent_memory_tool": update_agent_memory_tool_interface,
	"get_trending_token_from_coingecko_tool": get_trending_token_from_coingecko_tool_interface,
	"get_detail_of_token_from_coingecko_tool": get_detail_of_token_from_coingecko_tool_interface,
	"get_all_of_token_from_coingecko_tool": get_all_of_token_from_coingecko_tool_interface,
	"get_market_chart_of_token_from_coingecko_tool": get_market_chart_of_token_from_coingecko_tool_interface,
	"get_news_from_cryptopanic_tool": get_news_from_cryptopanic_tool_interface,
	"retrieve_agent_memory_tool": retrieve_agent_memory_tool_interface,
	"ask_gemini_tool": ask_gemini_tool_interface,
	"publish_content_to_avoca_tool": publish_content_to_avoca_tool_interface
}
