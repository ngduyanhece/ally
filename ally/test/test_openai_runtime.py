
from ally.runtimes.openai import OpenAIRuntime
from ally.utils.internal_data import InternalDataFrame
from app.core.settings import settings
from app.logger import get_logger

logger = get_logger(__name__)

def test_process_batch():
	df = InternalDataFrame(
		[['Hello', 'Yes'],
		 ['Test', 'No']],
		columns=['text', 'comments']
	)

	runtime = OpenAIRuntime(
		verbose=True,
		api_key=settings.openai_api_key,
		gpt_model_name="gpt-3.5-turbo",
	)
	result = runtime.process_batch(
		batch=df,
		input_template="{text} {comments}",
		output_template=[
			{
				"name": "answer",
				"description": "answer to the user's question"
			}
		],
		instructions='this is the test',
	)
	assert isinstance(result, InternalDataFrame)