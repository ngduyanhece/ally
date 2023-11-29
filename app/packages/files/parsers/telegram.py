
from app.modules.file.entity.files import FileEntity
from app.packages.files.loaders.telegram import TelegramChatFileLoader


def process_telegram(
	process_file,
	file: FileEntity,
	brain_id,
):
	return process_file(
		file=file,
		loader_class=TelegramChatFileLoader,
		brain_id=brain_id,
	)
