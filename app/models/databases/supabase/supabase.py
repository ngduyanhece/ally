from app.logger import get_logger
from app.models.databases.supabase import Brain, UserUsage

logger = get_logger(__name__)

class SupabaseDB(
    Brain,
    UserUsage
):

    def __init__(self, supabase_client):
        self.db = supabase_client
        Brain.__init__(self, supabase_client)
        UserUsage.__init__(self, supabase_client)
