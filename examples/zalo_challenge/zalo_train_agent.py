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
	train_function = modal.Function.lookup("zalo-agent-learn", "zalo_agent_learn")
	# split data into chunks of 10
	chunks = [data[x:x + 20] for x in range(0, len(data), 20)]
	header = ["testcase_data_id", "text_input", "reference_output", "context", "teacher_feedback"]
	first = True             
	start_index = 6
	chunks = chunks[start_index:]
	for i, chunk in enumerate(tqdm(chunks)):
		ids = [data["testcase_data_id"] for data in chunk]
		print(f"Processing chunk {i + start_index}")
	# train the model
		results = []
		for result in train_function.map(ids):
			results.append(result)
		with open("examples/data/zalo_math_agent_train_log_gpt35_turbo.csv", "a", encoding="utf-8") as f:
			writer = csv.writer(f)
			if first:
				writer.writerow(header)
				first = False
			for data, result in zip(chunks[i], results):
					writer.writerow([data["testcase_data_id"], data["text_input"], data["reference_output"], data["context"], result.assistant])

if __name__ == '__main__':
	train("examples/data/train_data.csv")