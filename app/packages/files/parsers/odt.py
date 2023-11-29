from langchain.document_loaders import UnstructuredPDFLoader

from app.modules.file.entity.files import FileEntity


def process_odt(process_file, file: FileEntity, brain_id):
	return process_file(
		file=file,
		loader_class=UnstructuredPDFLoader,
		brain_id=brain_id,
	)
