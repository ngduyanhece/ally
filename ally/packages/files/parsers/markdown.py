from langchain.document_loaders import UnstructuredMarkdownLoader

from app.modules.file.entity.files import FileEntity


def process_markdown(process_file, file: FileEntity, brain_id):
	return process_file(
		file=file,
		loader_class=UnstructuredMarkdownLoader,
		brain_id=brain_id,
	)
