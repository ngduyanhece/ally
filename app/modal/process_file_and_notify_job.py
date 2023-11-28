from pathlib import Path
from fastapi import UploadFile

import modal

from app.models.settings import get_supabase_client

ally_dir = Path(__file__).parent.parent.parent

image = modal.Image.debian_slim(
		python_version="3.10"
).pip_install(
	"fastapi==0.103.2",
	"langchain==0.0.325",
	"pydantic==2.4.2",
	"pydantic-settings==2.0.3",
	"supabase==1.1.1",
	"asyncpg==0.28.0",
	"python-multipart==0.0.6",
	"openai==0.28.1",
	"PyMuPDF==1.23.4",
	"tiktoken==0.5.1",
	"tqdm==4.66.1",
	"pandas==2.1.2"
)

stub = modal.Stub(
	name="file-process-and-notify",
	image=image,
	mounts=[
		modal.Mount.from_local_file(ally_dir / '.env', remote_path="/root/.env")
	],
)

@stub.function(
	image=image,
	retries=3,
	container_idle_timeout=50
)
def process_file_and_notify(
	file_name: str,
	file_original_name: str,
	brain_id,
	notification_id=None,
):
	try:
		supabase_client = get_supabase_client()
		tmp_file_name = "tmp-file-" + file_name
		tmp_file_name = tmp_file_name.replace("/", "_")

		with open(tmp_file_name, "wb+") as f:
			res = supabase_client.storage.from_("ally").download(file_name)
			f.write(res)
			f.seek(0)
			file_content = f.read()

			upload_file = UploadFile(
						file=f, filename=file_name.split("/")[-1], size=len(file_content)
				)

				file_instance = File(file=upload_file)
				loop = asyncio.get_event_loop()
				message = loop.run_until_complete(
						filter_file(
								file=file_instance,
								brain_id=brain_id,
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
	except Exception as e:
				notification_message = {
						"status": "error",
						"message": "There was an error uploading the file. Please check the file and try again. If the issue persist, please open an issue on Github",
						"name": file_instance.file.filename if file_instance.file else "",
				}
				update_notification_by_id(
						notification_id,
						NotificationUpdatableProperties(
								status=NotificationsStatusEnum.Done,
								message=str(notification_message),
						),
						)
				raise e  
	
	