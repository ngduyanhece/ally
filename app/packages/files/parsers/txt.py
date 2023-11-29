from langchain.document_loaders import TextLoader

from app.modules.file.entity.files import FileEntity


async def process_txt(
	process_file,
	file: FileEntity,
	brain_id,
):
	return await process_file(
		file=file,
		loader_class=TextLoader,
		brain_id=brain_id,
	)
