from typing import Dict

from langchain.document_loaders import Docx2txtLoader

from .common import process_file


def process_docx(
	file: Dict,
	agent_name: str
):
	return process_file(
		file=file,
		loader_class=Docx2txtLoader,
		agent_name=agent_name,
	)
