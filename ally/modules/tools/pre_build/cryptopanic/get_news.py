# write the python function to get the news from cryptopanic
# https://cryptopanic.com/api/v1/posts/?auth_token=3b90a9b02a35590a4f3065e8cc81500949e8d234&currencies=BTC,ETH&kind=news
# the function accepts the following parameters: currencies, which is the list of the currencies, for example: BTC,ETH
async def get_news_from_cryptopanic_tool(currencies: str):
	# import the requests library
	import requests

	# define the URL
	url = "https://cryptopanic.com/api/v1/posts/?auth_token=3b90a9b02a35590a4f3065e8cc81500949e8d234&currencies=" + currencies + "&kind=news"
	# send the GET request
	response = requests.get(url)
	# extract the response
	response_json = response.json()
	# extract the posts from the response
	posts = response_json['results']
	# extract the title, url, source, published_at, and currencies from the posts
	news_list = list()
	for post in posts:
		news = dict()
		news['title'] = post['title']
		news['url'] = post['url']
		news['source'] = post['source']['title']
		news['published_at'] = post['published_at']
		news['currencies'] = post['currencies']
		# # get the content from the url of the news
		# news_content = requests.get(post['url'])
		# try:
		# 	news_content_json = news_content.json()
		# except Exception as e:
		# 	news_content_json = dict()
		# 	news_content_json['content'] = "error getting the content of the news"
		# news['content'] = news_content_json['content']
		news_list.append(news)
	return str(news_list)

get_news_from_cryptopanic_tool_interface = {
	"type": "function",
	"function": {
		"name": "get_news_from_cryptopanic_tool",
		"description": "get the news from cryptopanic",
		"parameters": {
			"type": "object",
			"properties": {
				"currencies": {
					"type": "string",
					"description": "The currencies of the news for example: BTC,ETH",
				}
			},
			"required": ["currencies"]
		},
	}
}
