from langchain.document_loaders.epub import UnstructuredEPubLoader

from app.modules.file.entity.files import FileEntity


def process_epub(process_file, file: FileEntity, brain_id):
	return process_file(
		file=file,
		loader_class=UnstructuredEPubLoader,
		brain_id=brain_id,
	)
