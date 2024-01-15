from typing import Dict

from langchain.document_loaders import UnstructuredMarkdownLoader

from .common import process_file


def process_markdown(
	file: Dict,
	agent_name: str
):
	return process_file(
		file=file,
		loader_class=UnstructuredMarkdownLoader,
		agent_name=agent_name,
	)
