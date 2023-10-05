from concurrent.futures import ThreadPoolExecutor
from typing import List
from uuid import UUID

from app.logger import get_logger
from app.models.settings import get_supabase_db

logger = get_logger(__name__)

def process_batch(batch_ids: List[str]):
    supabase_db = get_supabase_db()

    try:
        if len(batch_ids) == 1:
            return (supabase_db.get_vectors_by_batch(UUID(batch_ids[0]))).data
        else:
            return (supabase_db.get_vectors_in_batch(batch_ids)).data
    except Exception as e:
        logger.error("Error retrieving batched vectors", e)


def get_unique_files_from_vector_ids(vectors_ids: List[str]):
    # Move into Vectors class
    """
    Retrieve unique user data vectors.
    """

    # constants
    BATCH_SIZE = 5

    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(vectors_ids), BATCH_SIZE):
            batch_ids = vectors_ids[i : i + BATCH_SIZE]
            future = executor.submit(process_batch, batch_ids)
            futures.append(future)

        # Retrieve the results
        vectors_responses = [future.result() for future in futures]

    documents = [item for sublist in vectors_responses for item in sublist]
    unique_files = [dict(t) for t in set(tuple(d.items()) for d in documents)]
    return unique_files
