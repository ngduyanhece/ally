import asyncio
import os

from celery import Celery
from fastapi import UploadFile

from app.core.settings import settings
from app.models.databases.supabase.notifications import \
    NotificationUpdatableProperties
from app.models.files import File
from app.models.notifications import NotificationsStatusEnum
from app.models.settings import get_supabase_client
from app.repository.brain.update_brain_last_update_time import \
    update_brain_last_update_time
from app.repository.notification.update_notification import \
    update_notification_by_id
from app.utils.processors import filter_file

CELERY_BROKER_URL = settings.celery_broker_url
CELERY_BROKER_QUEUE_NAME = settings.celery_broker_queue_name

if CELERY_BROKER_URL.startswith("sqs"):
    broker_transport_options = {
        CELERY_BROKER_QUEUE_NAME: {
            "my-q": {
                "url": CELERY_BROKER_URL,
            }
        }
    }
    celery = Celery(
        __name__,
        broker=CELERY_BROKER_URL,
        task_serializer="json",
        task_concurrency=4,
        worker_prefetch_multiplier=1,
        broker_transport_options=broker_transport_options,
    )
    celery.conf.task_default_queue = CELERY_BROKER_QUEUE_NAME
elif CELERY_BROKER_URL.startswith("redis"):
    celery = Celery(
        __name__,
        broker=CELERY_BROKER_URL,
        backend=CELERY_BROKER_URL,
        task_concurrency=4,
        worker_prefetch_multiplier=1,
        task_serializer="json",
    )
else:
    raise ValueError(f"Unsupported broker URL: {CELERY_BROKER_URL}")


@celery.task(name="process_file_and_notify")
def process_file_and_notify(
    file_name: str,
    file_original_name: str,
    enable_summarization,
    brain_id,
    openai_api_key,
    notification_id=None,
):
    supabase_client = get_supabase_client()
    tmp_file_name = "tmp-file-" + file_name
    tmp_file_name = tmp_file_name.replace("/", "_")

    with open(tmp_file_name, "wb+") as f:
        res = supabase_client.storage.from_("ally").download(file_name)
        f.write(res)
        f.seek(0)
        file_content = f.read()

        # file_object = io.BytesIO(file_content)
        upload_file = UploadFile(
            file=f, filename=file_name.split("/")[-1], size=len(file_content)
        )

        file_instance = File(file=upload_file)
        loop = asyncio.get_event_loop()
        message = loop.run_until_complete(
            filter_file(
                file=file_instance,
                enable_summarization=enable_summarization,
                brain_id=brain_id,
                openai_api_key=openai_api_key,
                original_file_name=file_original_name,
            )
        )

        f.close()
        os.remove(tmp_file_name)

        if notification_id:
            notification_message = {
                "status": message["type"],
                "message": message["message"],
                "name": file_instance.file.filename if file_instance.file else "",
            }
            update_notification_by_id(
                notification_id,
                NotificationUpdatableProperties(
                    status=NotificationsStatusEnum.Done,
                    message=str(notification_message),
                ),
            )
        update_brain_last_update_time(brain_id)

        return True
