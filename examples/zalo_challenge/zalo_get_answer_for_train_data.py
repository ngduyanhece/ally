
import csv
import json

import modal
from tqdm import tqdm

from app.models.chats import BrainAgentInput

DATA_PATH = 'examples/data/math_train.json'
CHAT_ID = "f16fd0b5-3e26-4f9e-8dcc-871832a436cc"
BRAIN_ID = "3e467f36-84fb-4257-837e-74da7def149a"


def load_json_data(data_path):
		with open(data_path, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return data["data"]

def convert_to_chat_input(data: dict) -> BrainAgentInput:
	question = data["question"]
	choices = data["choices"]
	text_input = f"QUESTION: {question} CHOICES:{choices}"

	return BrainAgentInput(
		text_input=text_input
	)

def generate_answer_for_train(data_path):
	json_data = load_json_data(data_path)
	predict_function = modal.Function.lookup("zalo-agent-chat", "zalo_agent_chat")
	data_to_modal = [convert_to_chat_input(data) for data in json_data]
	# split data into chunks of 10
	chunks = [data_to_modal[x:x + 10] for x in range(0, len(data_to_modal), 10)]
	# split json_data into chunks of 10
	json_chunks = [json_data[x:x + 10] for x in range(0, len(json_data), 10)]
	header = ["id", "question", "choices", "prediction", "answer"]
	first = True             
	start_index = 47
	chunks = chunks[start_index:]
	json_chunks = json_chunks[start_index:]             
	for i, chunk in enumerate(tqdm(chunks)):
		print(f"Processing chunk {i + start_index}")
		results = []
		for result in predict_function.map(chunk):
			results.append(result)
		with open("examples/data/math_train_result.csv", "a", encoding="utf-8") as f:
			writer = csv.writer(f)
			if first:
				writer.writerow(header)
				first = False
			for data, result in zip(json_chunks[i], results):
					writer.writerow([data["id"], data["question"], data["choices"], result.assistant, data["answer"]])

if __name__ == '__main__':
	generate_answer_for_train(DATA_PATH)