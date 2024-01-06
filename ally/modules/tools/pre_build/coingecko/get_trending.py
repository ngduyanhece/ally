
async def get_trending_token_from_coingecko_tool():
	from pycoingecko import CoinGeckoAPI
	cg = CoinGeckoAPI()
	response = cg.get_search_trending()
	# parsing the response into the list of trending coins with the following format:
	trending_coins = response['coins']
	coin_data_list = list()
	for coin in trending_coins:
		coin_data = dict()
		coin_data['id'] = coin['item']['id']
		coin_data['name'] = coin['item']['name']
		coin_data['symbol'] = coin['item']['symbol']
		coin_data['market_cap_rank'] = coin['item']['market_cap_rank']
		coin_data['coin_image'] = coin['item']['small']
		coin_data['score'] = coin['item']['score']
		coin_data['price_usd'] = coin['item']['data']['price']
		coin_data['market_cap'] = coin['item']['data']['market_cap']
		coin_data['total_volume'] = coin['item']['data']['total_volume']
		coin_data['7days_sparkline'] = coin['item']['data']['sparkline']
		coin_data_list.append(coin_data)
	return str(coin_data_list)

get_trending_token_from_coingecko_tool_interface = {
	"type": "function",
	"function": {
		"name": "get_trending_token_from_coingecko_tool",
		"description": "get the trending token from coingecko",
		"parameters": {
			"type": "object",
			"properties": {
			},
			"required": []
		},
	}
}