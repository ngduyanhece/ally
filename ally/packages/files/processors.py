import os

from chainlit import File

from .parsers.csv import process_csv
from .parsers.docx import process_docx
from .parsers.epub import process_epub
from .parsers.html import process_html
from .parsers.markdown import process_markdown
from .parsers.odt import process_odt
from .parsers.pdf import process_pdf
from .parsers.powerpoint import process_powerpoint
from .parsers.txt import process_txt
from .parsers.xlsx import process_xlsx

file_processors = {
	".txt": process_txt,
	".csv": process_csv,
	".md": process_markdown,
	".markdown": process_markdown,
	".pdf": process_pdf,
	".html": process_html,
	".pptx": process_powerpoint,
	".docx": process_docx,
	".odt": process_odt,
	".xlsx": process_xlsx,
	".xls": process_xlsx,
	".epub": process_epub,
}


def create_response(message, type):
  	return {"message": message, "type": type}


async def filter_file(
	file_element: File,
	agent_name: str,
):
	file_extension = os.path.splitext(file_element.name)[-1].lower()
	if file_extension in file_processors:
		try:
			result = await file_processors[file_extension](
				file=file_element,
				agent_name=agent_name,
			)
			if result is None or result == 0:
				return create_response(
					"？ There might have been an error while reading it, please make sure the file is not illformed or just an image",
					"warning",
				)
			return create_response(
				f"✅ file {file_element.name} has been uploaded to agent's memory",
				"success",
			)
		except Exception as e:
			return create_response(
				f"⚠️ An error occurred while processing the file {file_element.name}. {e}",
				"error",
			)

	return create_response(
		f"❌ {file_extension} is not supported.",
		"error",
	)
