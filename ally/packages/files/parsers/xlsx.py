from langchain.document_loaders import UnstructuredExcelLoader

from app.modules.file.entity.files import FileEntity


def process_xlsx(
	process_file,
	file: FileEntity,
	brain_id,
):
	return process_file(
		file=file,
		loader_class=UnstructuredExcelLoader,
		brain_id=brain_id,
	)
