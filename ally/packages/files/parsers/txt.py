from langchain.document_loaders import TextLoader

from app.modules.file.entity.files import FileEntity


def process_txt(process_file, file: FileEntity, brain_id):
  	return process_file(
		file=file,
		loader_class=TextLoader,
		brain_id=brain_id,
	)