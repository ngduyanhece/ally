from app.logger import get_logger
from app.models.databases.supabase import (ApiKeyHandler, Brain, Chats, Emoji,
                                           File, Knowledges, MetaBrain,
                                           Notifications, Onboarding, Prompts,
                                           TaskGoal, TestCaseData, UserUsage,
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
    File,
    Emoji,
    TestCaseData,
    TaskGoal,
    Onboarding
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
        Emoji.__init__(self, supabase_client)
        TestCaseData.__init__(self, supabase_client)
        TaskGoal.__init__(self, supabase_client)
        Onboarding.__init__(self, supabase_client)
