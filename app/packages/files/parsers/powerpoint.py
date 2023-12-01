from langchain.document_loaders import UnstructuredPowerPointLoader

from app.modules.file.entity.files import FileEntity


def process_powerpoint(process_file, file: FileEntity, brain_id):
	return process_file(
		file=file,
		loader_class=UnstructuredPowerPointLoader,
		brain_id=brain_id,
	)
