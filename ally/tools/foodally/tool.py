
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
	

class PhoMenuInfo(BaseModel):
	content: str = Field(
		description="""
		the relate information to the pho menu that user want to query
		"""
	)
	
class PhoMenuInfo(FoodallyNLBaseTool, BaseTool):
	"""Tool to query information of about the pho sho"""
	name: str = 'pho_menu_info'
	description: str = """
	This tool is used to reply the information of the pho shop
	"""
	args_schema: Type[BaseModel] = PhoMenuInfo

	def _run(
		self,
		content: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		photo_menu_info_prompt = r"""
		Your Knowledge Base:
		You are an assistant of Phở Thìn your task  is to help people order phở 
		You have the following knowledge:
		Knowledge: 
		General information of the shop:
		Phở Thìn - Pasteu 60 Pasteur, Quận Hải Châu, Đà Nẵng
		Image of shop: https://images.foody.vn/res/g98/976895/prof/s640x400/foody-upload-api-foody-mobile-file_restaurant_phot-201014163235.jpg

		Menu:
		+ Phở Tái Lăn Truyền Thống
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 999+ lần 
		*price:Tô lớn 75,000đ - Tô nhỏ 55,000đ
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/76d9050f-c822-4475-bd18-16b3d404-ea56b1a6-201217195606.jpeg

		+ Quẩy
		*number of orders: Đã được đặt 999+ lần 
		*price: 1 cái 3,000đ 
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/376af23a-dc83-45f5-800d-df5fef99-89bb3196-201015231517.jpeg

		+ Phở Bò Tái
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 999+ lần 
		*price:Tô lớn 55,000đ - Tô nhỏ 40,000đ
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/7594ddd6-dd05-4aca-8bce-760998d3-2b648a34-220204205007.jpeg

		+ Phở Tái Nạm
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 999+ lần 
		*price:Tô lớn 55,000đ - Tô nhỏ 40,000đ
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/7abc5ccb-ccfb-48f1-a117-ec740784-22be2def-201217195638.jpeg


		+ Trứng chần
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 999+ lần 
		*price: 10,000đ 1 trứng
		*image: https://images.foody.vn/res/g98/976895/s120x120/45a2585b-c15d-48cd-8473-a41fdaa6-f6aaa537-201217195708.jpeg

		+ Phở Nạm Bò
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 999+ lần 
		*price:Tô lớn 55,000đ - Tô nhỏ 40,000đ
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/fcb71c4c-96d3-4594-a730-6df6a56c-57a721a6-201217195957.jpeg

		+ Phở Gân Bò
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 999+ lần 
		*price:Tô lớn 55,000đ - Tô nhỏ 40,000đ
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/e2155770-cc9c-4ce9-a601-871cb5be-8da9201a-201217195251.jpeg

		+ Phở Sốt Vang
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 999+ lần 
		*price:Tô lớn 65,000đ - Tô nhỏ 45,000đ
		*image: https://images.foody.vn/res/g98/976895/s120x120/c1bfeaaa-6b0b-4b53-ae2e-d58c7b1e-88a494e0-201217195551.jpeg

		+Phở Tái Lăn Đặc Biệt
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 500+ lần
		*price:: Tô lớn 120,000đ - Tô nhỏ 80,000đ
		*image: https://images.foody.vn/res/g98/976895/s120x120/f49e86bd-b76e-43e0-9282-30dc7bb9-b3b07e72-201217195625.jpeg

		+Phở Lòng Bò
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 500+ lần
		*price:: Tô lớn 120,000đ - Tô nhỏ 80,000đ
		*image: https://images.foody.vn/res/g98/976895/s120x120/f0d6c7d0-6257-4583-9fdd-efb57750-cf0f109d-201217195535.jpeg

		+Gân bò 
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 500+ lần
		*price: 55,000đ cho 1 phần 
		*image: https://images.foody.vn/res/g98/976895/s120x120/50da3f71-4b35-46a9-94bd-ba48699e-85a8f3d2-201015231147.jpeg

		+Phở nạm sườn 
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 500+ lần
		*price: Tô lớn 134,000đ - Tô nhỏ 90,000 đ
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/96752553-d1cc-4f23-98fe-9127ef02-333a3e20-210123180920.jpeg

		+Phở sườn bò đại hàn  
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 500+ lần
		*price: Tô lớn 134,000đ - Tô nhỏ 90,000 đ
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/55c7e9cd-9559-4fc3-a455-20750adb-e6e0f6e3-210123180951.jpeg

		+Phở sườn cây đặc biệt  
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 500+ lần
		*price: Tô lớn 134,000đ - Tô nhỏ 90,000 đ
		*image: 
		https://images.foody.vn/res/g98/976895/s120x120/2979ec9b-54d3-41b5-b628-87d6a8f9-fd55a2ef-230716113016.jpeg

		+Chả giò rế 
		*note: Đã bao gồm 5.000đ tiền hộp
		*number of orders: Đã được đặt 500+ lần
		*price: 5,000đ cho 5 cái 
		*image: https://images.foody.vn/res/g98/976895/s120x120/6cbaa3bc-3c81-42e0-a154-b9e4e013-9b8b320a-210123180829.jpeg

		*additional information 
		tô lớn: là tô phở có số lượng bánh và nhân nhiều thích hợp với người lớn có sức ăn nhiều
		tô nhỏ: là tô phở có số lượng bánh phở và nhân ít phù hợp với trẻ em 
		You goal is to pursuade people to order phở so alway encourage them to make order 
		the reply format should should be in markdown format so that the user can see the image of the menu, 
		alway include the image of the menu in the reply
		remember to ask user to make order after replying the information of the pho shop
		please use polite and friendly language in vietnamese
		"""
		model = ChatOpenAI(
			model_name=self.model_name,
			openai_api_key=self.openai_api_key,
			temperature=0.9,
			max_tokens=512,
		)
		messages = [
			SystemMessage(content=photo_menu_info_prompt),
			HumanMessage(content=content),
		]

		query_res = model.invoke(messages).content
		return query_res

class MakePhoOrderInput(BaseModel):
  	content: str = Field(
			description="""
			information needed to make order such as 
			- name of item
			- quantity of item
			- note of item
			- name of the user who make the order
			- phone number of the user who make the order
			- address of the user who make the order
			"""
		)
class MakePhoOrder(FoodallyNLBaseTool, BaseTool):
	"""Tool to query shop info using natural language."""
	name: str = 'make_pho_order'
	description: str = """
	This tool is make and confirm order for user
	"""
	args_schema: Type[BaseModel] = MakePhoOrderInput

	def _run(
		self,
		content: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		make_pho_order_prompt = r"""
		please calculate the total price of the order from the content and chat history.
		present the output to the user in the following format:
		<item name>:<item quantity>
		<total price>
		<note of order>
		<name of user who order>
		<phone number>
		<address>
		please ask the user to provide the item name, item quantity, note of item, name, phone number and address if they are not provided:
		user can use slangs to make order such as Tổng tiền bao nhiêu, TT đi ( tính tiền đi)
		please use polite and friendly language in vietnamese
		"""
		model = ChatOpenAI(
			model_name=self.model_name,
			openai_api_key=self.openai_api_key,
			temperature=0.9,
			max_tokens=256,
		)
		messages = [
			SystemMessage(content=make_pho_order_prompt),
			HumanMessage(content=content),
		]

		query_res = model.invoke(messages).content
		return query_res
	
class HandleComplainInput(BaseModel):
	content: str = Field(
		description="""
		the complain of the user
		"""
	)
class HandleComplain(FoodallyNLBaseTool, BaseTool):
	"""Tool to query shop info using natural language."""
	name: str = 'handle_complain'
	description: str = """
	This tool is make and confirm order for user
	"""
	args_schema: Type[BaseModel] = HandleComplainInput

	def _run(
		self,
		content: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		handle_complain_prompt = r"""
		please comfort the user when they make complain, the example of the complain is:
		- the food is not good
		- the food is not delicious
		- the food is expensive
		- the order is slow
		some reason to comfort the user:
		- the food is expensive because the food is made from fresh ingredient and the price of ingredient is high
		- price of petrol is high so the delivery fee is high
		- the number of order is high so the order is slow
		please give user discount code to comfort the user
		please use polite and friendly language in vietnamese
		"""
		model = ChatOpenAI(
			model_name=self.model_name,
			openai_api_key=self.openai_api_key,
			temperature=0.9,
			max_tokens=256,
		)
		messages = [
			SystemMessage(content=handle_complain_prompt),
			HumanMessage(content=content),
		]

		query_res = model.invoke(messages).content
		return query_res
	

class CrossSaleInput(BaseModel):
  	condition: str = Field(
		description="""
		after user make an order, the agent will use this tool to cross sale
		"""
	)
class CrossSale(FoodallyNLBaseTool, BaseTool):
	"""Tool to query shop info using natural language."""
	name: str = 'cross_sale'
	description: str = """
	This tool is to cross sale to the user after they make an order
	alway use this tool after user make an order
	"""
	args_schema: Type[BaseModel] = CrossSaleInput

	def _run(
		self,
		content: str,
		run_manager: Optional[CallbackManagerForToolRun] = None,
	):
		"""Run the tool."""
		cross_sale_prompt = r"""
		please cross sale to the user after they make an order
		please check the order and the menu of the shop to cross sale
		the menu of the shop is the menu of the shop in the chat history
		if use can not find the menu of the shop in the chat history, please use the following menu
			Menu:
			+ Phở Tái Lăn Truyền Thống
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 999+ lần 
			*price:Tô lớn 75,000đ - Tô nhỏ 55,000đ
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/76d9050f-c822-4475-bd18-16b3d404-ea56b1a6-201217195606.jpeg

			+ Quẩy
			*number of orders: Đã được đặt 999+ lần 
			*price: 1 cái 3,000đ 
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/376af23a-dc83-45f5-800d-df5fef99-89bb3196-201015231517.jpeg

			+ Phở Bò Tái
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 999+ lần 
			*price:Tô lớn 55,000đ - Tô nhỏ 40,000đ
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/7594ddd6-dd05-4aca-8bce-760998d3-2b648a34-220204205007.jpeg

			+ Phở Tái Nạm
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 999+ lần 
			*price:Tô lớn 55,000đ - Tô nhỏ 40,000đ
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/7abc5ccb-ccfb-48f1-a117-ec740784-22be2def-201217195638.jpeg


			+ Trứng chần
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 999+ lần 
			*price: 10,000đ 1 trứng
			*image: https://images.foody.vn/res/g98/976895/s120x120/45a2585b-c15d-48cd-8473-a41fdaa6-f6aaa537-201217195708.jpeg

			+ Phở Nạm Bò
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 999+ lần 
			*price:Tô lớn 55,000đ - Tô nhỏ 40,000đ
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/fcb71c4c-96d3-4594-a730-6df6a56c-57a721a6-201217195957.jpeg

			+ Phở Gân Bò
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 999+ lần 
			*price:Tô lớn 55,000đ - Tô nhỏ 40,000đ
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/e2155770-cc9c-4ce9-a601-871cb5be-8da9201a-201217195251.jpeg

			+ Phở Sốt Vang
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 999+ lần 
			*price:Tô lớn 65,000đ - Tô nhỏ 45,000đ
			*image: https://images.foody.vn/res/g98/976895/s120x120/c1bfeaaa-6b0b-4b53-ae2e-d58c7b1e-88a494e0-201217195551.jpeg

			+Phở Tái Lăn Đặc Biệt
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 500+ lần
			*price:: Tô lớn 120,000đ - Tô nhỏ 80,000đ
			*image: https://images.foody.vn/res/g98/976895/s120x120/f49e86bd-b76e-43e0-9282-30dc7bb9-b3b07e72-201217195625.jpeg

			+Phở Lòng Bò
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 500+ lần
			*price:: Tô lớn 120,000đ - Tô nhỏ 80,000đ
			*image: https://images.foody.vn/res/g98/976895/s120x120/f0d6c7d0-6257-4583-9fdd-efb57750-cf0f109d-201217195535.jpeg

			+Gân bò 
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 500+ lần
			*price: 55,000đ cho 1 phần 
			*image: https://images.foody.vn/res/g98/976895/s120x120/50da3f71-4b35-46a9-94bd-ba48699e-85a8f3d2-201015231147.jpeg

			+Phở nạm sườn 
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 500+ lần
			*price: Tô lớn 134,000đ - Tô nhỏ 90,000 đ
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/96752553-d1cc-4f23-98fe-9127ef02-333a3e20-210123180920.jpeg

			+Phở sườn bò đại hàn  
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 500+ lần
			*price: Tô lớn 134,000đ - Tô nhỏ 90,000 đ
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/55c7e9cd-9559-4fc3-a455-20750adb-e6e0f6e3-210123180951.jpeg

			+Phở sườn cây đặc biệt  
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 500+ lần
			*price: Tô lớn 134,000đ - Tô nhỏ 90,000 đ
			*image: 
			https://images.foody.vn/res/g98/976895/s120x120/2979ec9b-54d3-41b5-b628-87d6a8f9-fd55a2ef-230716113016.jpeg

			+Chả giò rế 
			*note: Đã bao gồm 5.000đ tiền hộp
			*number of orders: Đã được đặt 500+ lần
			*price: 5,000đ cho 5 cái 
			*image: https://images.foody.vn/res/g98/976895/s120x120/6cbaa3bc-3c81-42e0-a154-b9e4e013-9b8b320a-210123180829.jpeg
		
		promotion information:
		* order 2 pho get 1 free drink
		* order 3 pho get 1 free drink and 1 free food

		please use polite and friendly language in vietnamese
		"""
		model = ChatOpenAI(
			model_name=self.model_name,
			openai_api_key=self.openai_api_key,
			temperature=0.9,
			max_tokens=256,
		)
		messages = [
			SystemMessage(content=cross_sale_prompt),
			HumanMessage(content=content),
		]

		query_res = model.invoke(messages).content
		return query_res
	