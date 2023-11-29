from langchain.document_loaders import PythonLoader

from app.modules.file.entity.files import FileEntity


async def process_python(process_file, file: FileEntity, brain_id):
	return await process_file(
		file=file,
		loader_class=PythonLoader,
		brain_id=brain_id,
	)
