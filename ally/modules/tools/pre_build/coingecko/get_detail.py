async def get_detail_of_token_from_coingecko_tool(id: str):
	from pycoingecko import CoinGeckoAPI
	cg = CoinGeckoAPI()
	response = cg.get_coin_by_id(
		id=id,
		localization="false",
		tickers="false",
		market_data="true",
		community_data="false",
		developer_data="false",
	)
	return str(response)

get_detail_of_token_from_coingecko_tool_interface = {
	"type": "function",
	"function": {
		"name": "get_detail_of_token_from_coingecko_tool",
		"description": "get the detail of token from coingecko",
		"parameters": {
			"type": "object",
			"properties": {
				"id": {
					"type": "string",
					"description": "The ids of the token for example: bitcoin, this ids can be find in the get_trending_token_from_coingecko_tool or get_all_of_token_from_coingecko_tool",
				}
			},
			"required": ["ids"]
		},
	}
}