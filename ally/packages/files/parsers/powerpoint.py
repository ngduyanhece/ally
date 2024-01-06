from typing import Dict

from langchain.document_loaders import UnstructuredPowerPointLoader

from .common import process_file


def process_powerpoint(
	file: Dict,
	agent_name: str
):
	return process_file(
		file=file,
		loader_class=UnstructuredPowerPointLoader,
		agent_name=agent_name,
	)
