from typing import Dict

from langchain.document_loaders import UnstructuredExcelLoader

from .common import process_file


def process_xlsx(
	file: Dict,
	agent_name: str
):
	return process_file(
		file=file,
		loader_class=UnstructuredExcelLoader,
		agent_name=agent_name,
	)
