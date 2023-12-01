import pandas as pd

from ally.agents.base import Agent
from ally.datasets.dataframe import DataFrameDataset
from ally.environments.base import BasicEnvironment
from ally.runtimes.openai import OpenAIRuntime
from ally.skills.collection.classification import ClassificationSkill
from app.core.settings import settings


def test_classification_skill():

	print("=> Initialize datasets ...")
	# Train dataset
	train_df = pd.DataFrame([
		["It was the negative first impressions, and then it started working.", "Positive"],
		["Not loud enough and doesn't turn on like it should.", "Negative"],
		["I don't know what to say.", "Neutral"],
	], columns=["text", "ground_truth"])

	# Test dataset
	test_df = pd.DataFrame([
		"All three broke within two months of use.",
		"The device worked for a long time, can't say anything bad.",
		"Just a random line of text.",
	], columns=["text"])
	train_dataset = DataFrameDataset(df=train_df)
	test_dataset = DataFrameDataset(df=test_df)

	openai_runtime = OpenAIRuntime(
		verbose=True,
		api_key=settings.openai_api_key,
		gpt_model_name="gpt-3.5-turbo",
	)
	basic_environment = BasicEnvironment(
		ground_truth_dataset=train_dataset,
		ground_truth_columns={"sentiment": "ground_truth"}
	)
	classification_skill = ClassificationSkill(
		name='sentiment',
		instruction_template="Label text as subjective or objective.",
		labels=["Positive", "Negative", "Neutral"],
		input_template="{text}",
	)
	
	agent = Agent(
		runtimes={
			'openai': openai_runtime
		},
		teacher_runtimes={
			'openai': openai_runtime
		},
		# connect to a dataset
		environment=basic_environment,
		# define a skill
		skills=classification_skill,
	)
	run = agent.learn(learning_iterations=3, accuracy_threshold=0.95)
	# assert run.get_accuracy()['sentiment'] > 0.8
	# print('\n\n=> Final instructions:')
	# print('=====================')
	# print(f'{agent.skills["sentiment"].instructions}')
	# print('=====================')
