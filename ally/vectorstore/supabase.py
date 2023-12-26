from typing import Any, List

from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase.client import Client


class CustomSupabaseVectorStore(SupabaseVectorStore):
	"""A custom vector store that uses the match_vectors table instead of the vectors table."""

	agent_id: str = "none"

	def __init__(
		self,
		client: Client,
		embedding: Embeddings,
		table_name: str,
		agent_id: str = "none",
	):
		super().__init__(client, embedding, table_name)
		self.agent_id = agent_id

	def similarity_search(
		self,
		query: str,
		k: int = 2,
		table: str = "match_vectors",
		threshold: float = 0.5,
		**kwargs: Any
	) -> List[Document]:
		vectors = self._embedding.embed_documents([query])
		query_embedding = vectors[0]
		res = self._client.rpc(
			table,
			{
				"query_embedding": query_embedding,
				"match_count": k,
				"p_agent_id": str(self.agent_id),
			},
		).execute()

		match_result = [
			(
				Document(
					metadata=search.get("metadata", {}),  # type: ignore
					page_content=search.get("content", ""),
				),
				search.get("similarity", 0.0),
			)
			for search in res.data
			if search.get("content")
		]

		documents = [doc for doc, _ in match_result]

		return documents