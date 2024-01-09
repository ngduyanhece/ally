async def get_market_chart_of_token_from_coingecko_tool(id: str, days: str):
	from pycoingecko import CoinGeckoAPI
	cg = CoinGeckoAPI()
	response = cg.get_coin_market_chart_by_id(
		id=id,
		vs_currency="usd",
		days=days,
	)
	return str(response)


get_market_chart_of_token_from_coingecko_tool_interface = {
	"type": "function",
	"function": {
		"name": "get_market_chart_of_token_from_coingecko_tool",
		"description": "get the market chart of token from coingecko",
		"parameters": {
			"type": "object",
			"properties": {
				"id": {
					"type": "string",
					"description": "The ids of the token for example: bitcoin, this ids can be find in the get_trending_token_from_coingecko_tool or get_all_of_token_from_coingecko_tool",
				},
				"days": {
					"type": "string",
					"description": "The days of the chart for example: 1, 7, 14, 30, 90, 180, 365, max",
				}
			},
			"required": ["id", "days"]
		},
	}
}