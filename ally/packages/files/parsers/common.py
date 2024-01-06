import json
import os
import tempfile
import time
from typing import Any, Dict

import pinecone
from core.settings import settings
from langchain.pydantic_v1 import Field
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from loguru import logger


class DocumentSerializable(Document):
	"""Class for storing a piece of text and associated metadata."""

	page_content: str
	metadata: dict = Field(default_factory=dict)

	@property
	def lc_serializable(self) -> bool:
		return True

	def __repr__(self):
		return f"Document(page_content='{self.page_content[:50]}...', metadata={self.metadata})"

	def __str__(self):
		return self.__repr__()

	def to_json(self) -> str:
		"""Convert the Document object to a JSON string."""
		return json.dumps(
			{
				"page_content": self.page_content,
				"metadata": self.metadata,
			}
		)

def compute_documents(
	file: Dict,
	loader_class: Any,
	chunk_size=4000,
	chunk_overlap=200,
):
	"""
	Compute the documents from the file

	Args:
			loader_class (class): The class of the loader to use to load the file
	"""
	logger.info(f"Computing documents from file {file.name}")

	documents = []
	with tempfile.NamedTemporaryFile(
		delete=False,
		suffix=file.name
	) as tmp_file:
		tmp_file.write(file.content)
		tmp_file.flush()
		loader = loader_class(tmp_file.name)
		documents = loader.load()

	os.remove(tmp_file.name)

	text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
			chunk_size=chunk_size, chunk_overlap=chunk_overlap
	)
	documents = text_splitter.split_documents(documents)
	return documents


async def process_file(
	file: Dict,
	loader_class: Any,
	agent_name: str,
):
	
	documents = compute_documents(file, loader_class)
	dateshort = time.strftime("%Y%m%d")

	metadata = {
		"file_name": file.name,
		"chunk_size": 2000,
		"chunk_overlap": 200,
		"date": dateshort,
	}
	docs = []

	if documents is not None:
		for doc in documents:
			doc_with_metadata = DocumentSerializable(
				page_content=doc.page_content, metadata=metadata
			)
			docs.append(doc_with_metadata)
	
	pinecone.init(
		api_key=settings.pinecone_api_key, 
		environment=settings.pinecone_environment
	)
	index = pinecone.Index(agent_name)
	embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
	pinecone_vector_db = Pinecone(index, embeddings, "text")
	page_contents = [doc.page_content for doc in docs]
	# metadatas = [doc.metadata for doc in docs]
	try:
		ids = pinecone_vector_db.add_texts(
			texts=page_contents,
			batch_size=100,
			embedding_chunk_size=2000,
		)
	except Exception as e:
		raise e
	
	return ids
