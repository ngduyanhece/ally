async def get_all_of_token_from_coingecko_tool():
	from pycoingecko import CoinGeckoAPI
	cg = CoinGeckoAPI()
	response = cg.get_coins_list()
	return str(response)

get_all_of_token_from_coingecko_tool_interface = {
	"type": "function",
	"function": {
		"name": "get_all_of_token_from_coingecko_tool",
		"description": "get the list of all tokens from coingecko",
		"parameters": {
			"type": "object",
			"properties": {
			},
			"required": []
		},
	}
}