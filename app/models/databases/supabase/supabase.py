from app.logger import get_logger
from app.models.databases.supabase import (ApiKeyHandler, Brain, Chats, File,
                                           Knowledges, MetaBrain,
                                           Notifications, Prompts, UserUsage,
                                           Vector)

logger = get_logger(__name__)

class SupabaseDB(
    Brain,
    MetaBrain,
    UserUsage,
    Prompts,
    ApiKeyHandler,
    Chats,
    Notifications,
    Knowledges,
    Vector,
    File
):

    def __init__(self, supabase_client):
        self.db = supabase_client
        Brain.__init__(self, supabase_client)
        MetaBrain.__init__(self, supabase_client)
        UserUsage.__init__(self, supabase_client)
        Prompts.__init__(self, supabase_client)
        ApiKeyHandler.__init__(self, supabase_client)
        Chats.__init__(self, supabase_client)
        Notifications.__init__(self, supabase_client)
        Knowledges.__init__(self, supabase_client)
        Vector.__init__(self, supabase_client)
        File.__init__(self, supabase_client)
