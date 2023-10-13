from app.models.databases.supabase.notifications import \
    CreateNotificationProperties
from app.models.settings import get_supabase_db


def add_notification(notification: CreateNotificationProperties):
    """
    Add a notification
    """
    supabase_db = get_supabase_db()

    return supabase_db.add_notification(notification)
