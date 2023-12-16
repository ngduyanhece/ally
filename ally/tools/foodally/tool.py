
from typing import Optional, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from supabase.client import Client
from thefuzz import fuzz


class FoodallyBaseTool(BaseTool):
	"""
	Base tool for Foodally tools.
	"""
	db: Client = None

class QueryShopInfoByShopNameInput(BaseModel):
	shop_name_pattern: str = Field(description="search query to look up")

class QueryShopInfoByShopNameTool(FoodallyBaseTool, BaseTool):
	"""Tool to query shop info."""

	name: str = "query_shop_info"
	description: str = """
	This tool is used to query information of food shop
	the language used for this tool is Vietnamese
	"""
	args_schema: Type[BaseModel] = QueryShopInfoByShopNameInput

	def _run(
		self,
		shop_name_pattern: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	) -> str:
		"""Run the tool."""
		# get all the shop_name from shop_info table
		shop_name_list = self.db.from_('shop_info').select('shop_name').execute().data
		# # filter the shop_name with pattern
		shop_name_list = [
			shop_name['shop_name'] for shop_name in shop_name_list if fuzz.ratio(
				shop_name_pattern, shop_name['shop_name']) > 50]
		# get shop_info from shop_info table with shop_name in shop_name_list
		result = self.db.from_('shop_info').select('*').in_(
			'shop_name', shop_name_list).execute().data
		return str(result)


class RecommendShopByRatingInput(BaseModel):
  	pass

class RecommendShopByRating(FoodallyBaseTool, BaseTool):
	"""Tool to get food shop info order by rating of the  food shop."""
	name: str = 'recommend_shop_by_rating'
	description: str = """
	This tool is use to get top food shop by rating, this tool is
	use when user want to be recommend a food shop.
	this tool is the default tool of the agent if the agent do not have
	any information to provide to the user, please use this tool instead
	"""
	args_schema: Type[BaseModel] = RecommendShopByRatingInput

	def _run(
		self,
	):
		"""Run the tool."""
		# get all shop_info from shop_info table
		shop_info_list = self.db.from_('shop_info').select('*').execute().data
		# sort the shop_info_list by rating
		shop_info_list = sorted(shop_info_list, key=lambda x: x['rating'], reverse=True)[:3]
		return str(shop_info_list)


class QueryItemInfoByShopNameInput(BaseModel):
	shop_name_pattern: str = Field(description="search query to look up")
class QueryItemInfoByShopNameTool(FoodallyBaseTool, BaseTool):
	"""Tool to query food and drink info from a shop."""
	name: str = 'query_food_and_drink_info_by_shop_name'
	description: str = """
	This tool is used to query food and drink info from a particular shop
	this tool accept one parameter: shop_name_pattern, this is the name of the shop
	that user want to query food and drink info
	the language used for this tool is Vietnamese
	"""
	args_schema: Type[BaseModel] = QueryItemInfoByShopNameInput

	def _run(
		self,
		shop_name_pattern: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		# get list ids of shop with shop_name
		shop_name_list = self.db.from_('shop_info').select('shop_name').execute().data
		# filter the shop_name with pattern
		shop_name_list = [
			shop_name['shop_name'] for shop_name in shop_name_list if fuzz.ratio(
				shop_name_pattern, shop_name['shop_name']) > 40]
		# get food and drink info from shop with id of shop in shop_name_list
		food_and_drink_info_list = self.db.from_('items').select('*').in_(
			'shop_name', shop_name_list).execute().data
		return str(food_and_drink_info_list)

class QueryShopInfoByItemInput(BaseModel):
	items: list[str] = Field(description="list of food and drink name to look up the related shop")

class QueryShopInfoByItemTool(FoodallyBaseTool, BaseTool):
	"""Tool to query shop info by item name."""
	name: str = 'query_shop_info_by_item_name'
	description: str = """
	This tool is used to query shop info by item name, this tool accept one 
	parameter: items type list of str, this is the list of item name that user want to query which shop sell
	the language used for this tool is Vietnamese
	"""
	args_schema: Type[BaseModel] = QueryShopInfoByItemInput

	def _run(
		self,
		items: list,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		# get all the food and drink name from items table
		food_and_drink_name_list = self.db.from_('items').select('name').execute().data
		# get candidate food and drink name from items
		candidate_items = []
		for item in items:
			candidate_items.extend([
				food_and_drink_name['name'] for food_and_drink_name in food_and_drink_name_list if fuzz.ratio(
					item, food_and_drink_name['name']) > 50])
		candidate_shop_names = []
		# get all shop_name from items table which relate to candidate_items
		for candidate_item in candidate_items:
			candidate_shop_names.extend(self.db.from_('items').select('shop_name').eq(
				'name', candidate_item).execute().data)
		# get all shop_info from shop_info table which relate to candidate_shop_names
		shop_info_list = self.db.from_('shop_info').select('*').in_(
			'shop_name', candidate_shop_names).execute().data
		return str(shop_info_list)

class FoodallyNLBaseTool(BaseTool):
	"""
	Base tool for Foodally NL tools.
	"""
	openai_api_key: str = None
	model_name: str = None

class EstimatePriceInput(BaseModel):
	content: str = Field(description="the related information to the price of the food or drink")

class EstimatePrice(FoodallyNLBaseTool, BaseTool):
	"""Tool to query shop info using natural language."""
	name: str = 'estimate_price'
	description: str = """
	This tool is used to estimate the price of a food or drink or after user make an order
	this tool accept one parameter: content.
	the content is the name of foods or drink and the name of shop
	the language used for this tool is Vietnamese
	"""
	args_schema: Type[BaseModel] = EstimatePriceInput

	def _run(
		self,
		content: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		query_shop_info_prompt = r"""
		please calculate the total price of the following items included in the content:
		the unit of the price is the same as the unit of the price in the content
		please reply in vietnamese language with the following format:
		<item name>:<item quantity>
		<total price>
		content:
		"""
		model = ChatOpenAI(
			model_name=self.model_name,
			openai_api_key=self.openai_api_key,
			temperature=0.9,
			max_tokens=512,
		)
		messages = [
			SystemMessage(content=query_shop_info_prompt),
			HumanMessage(content=content),
		]

		query_res = model.invoke(messages).content
		return query_res


class MakeOrderInput(BaseModel):
  	content: str = Field(
			description="""the information of the order including the 
			name of the food and drink, the quantity of the food and drink,
			and the name of the shop
			the name of user who created the order
			the phone number of the user who created the order
			the address of the user who created the order
			the language used for this tool is Vietnamese
			the price should be get from the chat history
			"""
		)

class MakeOrder(FoodallyNLBaseTool, BaseTool):
	"""Tool to query shop info using natural language."""
	name: str = 'make_order'
	description: str = """
	This tool is make and confirm order for user
	"""
	args_schema: Type[BaseModel] = MakeOrderInput

	def _run(
		self,
		content: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		query_shop_info_prompt = r"""
		please calculate the total price from the content and chat history.
		you will inform the total price to the user after calculating the total price
		then please make and confirm the order base on the given content in format:
		<item name>:<item quantity>
		<name>
		<phone number>
		<address>
		please ask the user to provide the item name, item quantity, name, phone number and address if they are not provided:
		alway calculate the total price after the user provide the item name and item quantity then inform the user the total price
		"""
		model = ChatOpenAI(
			model_name=self.model_name,
			openai_api_key=self.openai_api_key,
			temperature=0.9,
			max_tokens=256,
		)
		messages = [
			SystemMessage(content=query_shop_info_prompt),
			HumanMessage(content=content),
		]

		query_res = model.invoke(messages).content
		return query_res



