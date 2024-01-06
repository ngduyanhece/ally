from typing import Dict

from langchain.document_loaders import UnstructuredHTMLLoader

from .common import process_file


def process_html(
	file: Dict,
	agent_name: str
):
	return process_file(
		file=file,
		loader_class=UnstructuredHTMLLoader,
		agent_name=agent_name,
	)
