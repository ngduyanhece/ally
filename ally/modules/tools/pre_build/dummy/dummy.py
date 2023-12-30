
def get_current_weather_tool(location: str, format: str):
	# return dummy weather
	return "The current weather in {} is {} degrees {}".format(location, 20, format)

get_current_weather_interface = {
	"type": "function",
	"function": {
		"name": "get_current_weather_tool",
		"description": "Get the current weather",
		"parameters": {
			"type": "object",
			"properties": {
				"location": {
					"type": "string",
					"description": "The city and state, e.g. San Francisco, CA",
				},
				"format": {
					"type": "string",
					"enum": ["celsius", "fahrenheit"],
					"description": "The temperature unit to use. Infer this from the users location.",
				},
			},
			"required": ["location", "format"],
		},
	}
}