import csv

import modal
from tqdm import tqdm


def load_train_data(data_path):
	# load csv file and return the data from data_path
	with open(data_path, 'r', encoding='utf-8') as f:
		reader = csv.DictReader(f)
		data = []
		for row in reader:
			data.append(row)
		return data

def train(data_path):
	# load data from data_path
	data = load_train_data(data_path)
	train_function = modal.Function.lookup("zalo-me-agent-learn", "zalo_me_agent_learn")
	# split data into chunks of 10
	chunks = [data[x:x + 10] for x in range(0, len(data), 10)]
	header = ["testcase_data_id", "text_input", "reference_output", "teacher_feedback"]
	first = True             
	start_index = 0
	end_index = 2
	chunks = chunks[start_index:end_index]
	for i, chunk in enumerate(tqdm(chunks)):
		ids = [data["testcase_data_id"] for data in chunk]
		print(f"Processing chunk {i + start_index}")
	# train the model
		results = []
		for result in train_function.map(ids):
			results.append(result)
		with open("examples/zalo_challenge/data/zalo_me_agent_train_log_gpt4.csv", "a", encoding="utf-8") as f:
			writer = csv.writer(f)
			if first:
				writer.writerow(header)
				first = False
			for data, result in zip(chunks[i], results):
					writer.writerow([data["testcase_data_id"], data["text_input"], data["reference_output"], result.assistant])

if __name__ == '__main__':
	train("examples/zalo_challenge/data/me_train_data.csv")