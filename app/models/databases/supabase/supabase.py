from app.logger import get_logger

logger = get_logger(__name__)

class SupabaseDB():
	def __init__(self, supabase_client):
		self.db = supabase_client
