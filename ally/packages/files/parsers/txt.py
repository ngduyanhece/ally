
from typing import Dict

from langchain.document_loaders import TextLoader

from .common import process_file


async def process_txt(
	file: Dict,
	agent_name: str,
):
	return await process_file(
		file=file,
		loader_class=TextLoader,
		agent_name=agent_name,
	)
