from typing import Dict

from langchain.document_loaders.epub import UnstructuredEPubLoader

from .common import process_file


def process_epub(
	file: Dict,
	agent_name: str
):
	return process_file(
		file=file,
		loader_class=UnstructuredEPubLoader,
		agent_name=agent_name,
	)
