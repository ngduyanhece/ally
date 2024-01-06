from typing import Dict

from langchain.document_loaders import CSVLoader

from .common import process_file


def process_csv(
	file: Dict,
	agent_name: str,
):
	return process_file(
		file=file,
		loader_class=CSVLoader,
		agent_name=agent_name,
	)
