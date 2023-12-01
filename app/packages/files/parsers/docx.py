from langchain.document_loaders import Docx2txtLoader

from app.modules.file.entity.files import FileEntity


def process_docx(process_file, file: FileEntity, brain_id):
	return process_file(
		file=file,
		loader_class=Docx2txtLoader,
		brain_id=brain_id,
	)
