from langchain.document_loaders import CSVLoader

from app.modules.file.entity.files import FileEntity


def process_csv(
	process_file,
	file: FileEntity,
	brain_id,
):
	return process_file(
		file=file,
		loader_class=CSVLoader,
		brain_id=brain_id,
	)
