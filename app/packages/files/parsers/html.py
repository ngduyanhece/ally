from langchain.document_loaders import UnstructuredHTMLLoader

from app.modules.file.entity.files import FileEntity


def process_html(process_file, file: FileEntity, brain_id):
	return process_file(
		file=file,
		loader_class=UnstructuredHTMLLoader,
		brain_id=brain_id,
	)