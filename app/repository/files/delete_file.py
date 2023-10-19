from multiprocessing import get_logger

from supabase.client import Client

from app.models import get_supabase_client

logger = get_logger()


def delete_file_from_storage(file_identifier: str):
    supabase_client: Client = get_supabase_client()

    try:
        response = supabase_client.storage.from_("ally").remove([file_identifier])
        return response
    except Exception as e:
        logger.error(e)
        raise e
