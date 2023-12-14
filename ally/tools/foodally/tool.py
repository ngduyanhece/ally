
from typing import Optional

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.tools.base import BaseTool
from supabase.client import Client
from thefuzz import fuzz


class FoodallyBaseTool(BaseTool):
	"""
	Base tool for Foodally tools.
	"""
	db: Client = None

class QueryShopInfoByShopNameTool(FoodallyBaseTool, BaseTool):
	"""Tool to query shop info."""
	name: str = 'query shop info by shop_name'
	description: str = """
	This tool is used to query information of food shop, this tool accept one 
	parameter: shop_name_pattern
	this parameter is the name of the shop that user want to query
	some valid patterns is like: "Buffet Nướng"
	the language used for this tool is Vietnamese
	"""

	def _run(
		self,
		shop_name_pattern: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		# get all the shop_name from shop_info table
		shop_name_list = self.db.from_('shop_info').select('shop_name').execute().data
		# filter the shop_name with pattern
		shop_name_list = [
			shop_name['shop_name'] for shop_name in shop_name_list if fuzz.ratio(
				shop_name_pattern, shop_name['shop_name']) > 50]
		# get shop_info from shop_info table with shop_name in shop_name_list
		shop_info_list = self.db.from_('shop_info').select('*').in_(
			'shop_name', shop_name_list).execute().data
		return shop_info_list
	
class RecommendShopByRating(FoodallyBaseTool, BaseTool):
	"""Tool to get food shop info order by rating of the  food shop."""
	name: str = 'recommend shop by rating'
	description: str = """
	This tool is use to get top food shop by rating, this tool is
	use when user want to be recommend a food shop
	"""

	def _run(
		self,
		pattern: str,
	):
		"""Run the tool."""
		# get all shop_info from shop_info table
		shop_info_list = self.db.from_('shop_info').select('*').execute().data
		# sort the shop_info_list by rating
		shop_info_list = sorted(shop_info_list, key=lambda x: x['rating'], reverse=True)[:3]
		return shop_info_list

class QueryItemInfoByShopNameTool(FoodallyBaseTool, BaseTool):
	"""Tool to query food and drink info from a shop."""
	name: str = 'query_food_and_drink_info by shop_name'
	description: str = """
	This tool is used to query food and drink info from a particular shop
	this tool accept one parameter: shop_name_pattern, this is the name of the shop
	that user want to query food and drink info
	the language used for this tool is Vietnamese
	"""

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
				shop_name_pattern, shop_name['shop_name']) > 50]
		# get food and drink info from shop with id of shop in shop_name_list
		food_and_drink_info_list = self.db.from_('items').select('*').in_(
			'shop_name', shop_name_list).execute().data
		return food_and_drink_info_list

class QueryShopInfoByItemTool(FoodallyBaseTool, BaseTool):
	"""Tool to query shop info by item name."""
	name: str = 'query_shop_info by item_name'
	description: str = """
	This tool is used to query shop info by item name, this tool accept one 
	parameter: items type list of str, this is the list of item name that user want to query which shop sell
	some valid patterns is like: "Bò nướng"
	the language used for this tool is Vietnamese
	"""

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
				food_and_drink_name['name'] for food_and_drink_name in food_and_drink_name_list if _fuzzy_match(
					item, food_and_drink_name['name'], 0.2)])
		candidate_shop_names = []
		# get all shop_name from items table which relate to candidate_items
		for candidate_item in candidate_items:
			candidate_shop_names.extend(self.db.from_('items').select('shop_name').eq(
				'name', candidate_item).execute().data)
		# get all shop_info from shop_info table which relate to candidate_shop_names
		shop_info_list = self.db.from_('shop_info').select('*').in_(
			'shop_name', candidate_shop_names).execute().data
		return shop_info_list


class FoodallyNLBaseTool(BaseTool):
	"""
	Base tool for Foodally NL tools.
	"""
	openai_api_key: str = None
	model_name: str = None


class EstimatePrice(FoodallyNLBaseTool, BaseTool):
	"""Tool to query shop info using natural language."""
	name: str = 'estimate_price'
	description: str = """
	This tool is used to estimate the price of a food or drink
	this tool accept one parameter: content.
	the content is the name of foods or drink and the name of shop
	the language used for this tool is Vietnamese
	"""

	def _run(
		self,
		content: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		query_shop_info_prompt = r"""
		please calculate the total price of the following items included in the content:
		the unit of the price is the same as the unit of the price in the content
		please reply in vietnamese language
		content:
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


class EntityResolution(FoodallyNLBaseTool, BaseTool):
	"""Tool to resolve entities in natural language. for example, resolve this in sentence"""
	name: str = 'resolve_entities'
	description: str = """
	This tool is used to resolve entities in natural language. it is used when model can 
	not detect the entities in the sentence
	this tool accept one parameter: memory.
	memory is the memory of the conversation between the agent and the user
	"""

	def _run(
		self,
		memory: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		resolute_entities_prompt = r"""
		please resolve the entities in the following sentence:
		please reply in vietnamese language
		content:
		"""
		model = ChatOpenAI(
			model_name=self.model_name,
			openai_api_key=self.openai_api_key,
			temperature=0.9,
			max_tokens=256,
		)
		messages = [
			SystemMessage(content=resolute_entities_prompt),
			HumanMessage(content=memory),
		]

		query_res = model.invoke(messages).content
		return query_res

class OderFood(FoodallyNLBaseTool, BaseTool):
	"""Tool to order food."""
	name: str = 'order_food'
	description: str = """
	This tool is used to order food
	this tool accept one parameter: memory.
	memory is the memory of the conversation between the agent and the user
	and the input from the user in case user does not mention the name of the shop
	"""

	def _run(
		self,
		memory: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		order_food_prompt = r"""
		please create a order for the following items
		you reply should be in the following format:
		<item name>:<item quantity>
		<total price>
		This is the items:
		"""
		model = ChatOpenAI(
			model_name=self.model_name,
			openai_api_key=self.openai_api_key,
			temperature=0.9,
			max_tokens=256,
		)
		messages = [
			SystemMessage(content=order_food_prompt),
			HumanMessage(content=memory),
		]

		query_res = model.invoke(messages).content
		return query_res