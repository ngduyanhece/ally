
from typing import Optional

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools.base import BaseTool
from supabase.client import Client

from ally.utils.matching import _fuzzy_match


class FoodallyBaseTool(BaseTool):
	"""
	Base tool for Foodally tools.
	"""
	db: Client = None

class QueryShopInfoByShopNameTool(FoodallyBaseTool, BaseTool):
	"""Tool to query shop info."""
	name: str = 'query_shop_info by shop_name'
	description: str = """
	This tool is used to query values from shop_info table
	this tool accept one parameter: pattern
	some valid patterns is like: "Buffet Nướng"
	the language used for this tool is Vietnamese
	"""

	def _run(
		self,
		pattern: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		# get all shop_name from  shop_info table
		shop_name_list = self.db.from_('shop_info').select('shop_name').execute().data
		# filter the shop_name with pattern
		shop_name_list = [shop_name['shop_name'] for shop_name in shop_name_list if _fuzzy_match(pattern, shop_name['shop_name'], 0.2)][:10]
		# get all shop_info with shop_name in shop_name_list
		shop_info_list = self.db.from_('shop_info').select('*').in_('shop_name', shop_name_list).execute().data
		return shop_info_list
	
class ShopInfoOrderByRating(FoodallyBaseTool, BaseTool):
	"""Tool to get food shop info order by rating of the  food shop."""
	name: str = 'shop_info order by rating'
	description: str = """
	This tool is use to get top food shop by rating, this tool is
	use when the question of user related to rating 
	"""

	def _run(
		self,
		pattern: str,
	):
		"""Run the tool."""
		# get all shop_info from shop_info table
		shop_info_list = self.db.from_('shop_info').select('*').execute().data
		# sort the shop_info_list by rating
		shop_info_list = sorted(shop_info_list, key=lambda x: x['rating'], reverse=True)[:100]
		return shop_info_list

class QueryItemInfoByShopNameTool(FoodallyBaseTool, BaseTool):
	"""Tool to query food and drink info from a shop."""
	name: str = 'query_food_and_drink_info by shop_name'
	description: str = """
	This tool is used to query food and drink info from a shop
	this tool accept one parameter: pattern. the pattern is name of shop
	the language used for this tool is Vietnamese
	"""

	def _run(
		self,
		pattern: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		# get list ids of shop with shop_name
		shop_name_list = self.db.from_('shop_info').select('shop_name').execute().data
		# filter the shop_name with pattern
		shop_name_list = [shop_name['shop_name'] for shop_name in shop_name_list if _fuzzy_match(pattern, shop_name['shop_name'], 0.2)][:10]
		# get food and drink info from shop with id of shop in shop_name_list
		shop_name_ids = self.db.from_('shop_info').select('shop_id').in_('shop_name', shop_name_list).execute().data
		shop_name_ids_list = [shop_name_id['shop_id'] for shop_name_id in shop_name_ids]
		food_and_drink_info_list = self.db.from_('item').select('*').in_('shop_id', shop_name_ids_list).execute().data
		return food_and_drink_info_list