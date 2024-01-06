from typing import Dict

from langchain.document_loaders import UnstructuredPDFLoader

from .common import process_file


def process_odt(
	file: Dict,
	agent_name: str
):
	return process_file(
		file=file,
		loader_class=UnstructuredPDFLoader,
		agent_name=agent_name,
	)
