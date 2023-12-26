from langchain.document_loaders import NotebookLoader

from app.modules.file.entity.files import FileEntity


def process_ipnyb(process_file, file: FileEntity, brain_id):
	return process_file(
		file=file,
		loader_class=NotebookLoader,
		brain_id=brain_id,
	)
