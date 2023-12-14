from typing import List

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool
from supabase.client import Client

from ally.tools.foodally.tool import (QueryItemInfoByShopNameTool,
                                      QueryShopInfoByShopNameTool,
                                      QueryShopInfoNL, ShopInfoOrderByRating)


class FoodallyToolkit(BaseToolkit):
	"""Toolkit for foodally agents.
	This is just a tool for demo and testing purposes so we put the key directly here.
	It is a extremely bad practice to put the key directly in the code and you should
	not do this in production.
	"""
	db: Client = None

	class Config:
		"""Configuration for this pydantic object."""
		arbitrary_types_allowed = True

	def get_tools(self) -> List[BaseTool]:
		"""Get the tools in the toolkit."""
		query_shop_info_by_shop_name_tool = QueryShopInfoByShopNameTool(db=self.db)
		query_shop_info_order_by_rating = ShopInfoOrderByRating(db=self.db)
		query_item_info_by_shop_name = QueryItemInfoByShopNameTool(db=self.db)
		return [
			query_shop_info_by_shop_name_tool,
			query_shop_info_order_by_rating,
			query_item_info_by_shop_name
		]

class FoodallyNLToolkit(BaseToolkit):
	"""Toolkit for foodally agents.
	This is just a tool for demo and testing purposes so we put the key directly here.
	It is a extremely bad practice to put the key directly in the code and you should
	not do this in production.
	"""
	openai_api_key: str = "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"
	model_name: str = "gpt-3.5-turbo"

	class Config:
		"""Configuration for this pydantic object."""
		arbitrary_types_allowed = True

	def get_tools(self) -> List[BaseTool]:
		"""Get the tools in the toolkit."""
		query_shop_info_nl = QueryShopInfoNL(
			openai_api_key=self.openai_api_key,
			model_name=self.model_name
		)
		return [
			query_shop_info_nl
		]
