import json

from tqdm import tqdm

from ally.utils.logs import print_text
from app.models.settings import get_supabase_db
from app.repository.dataset.add_testcase_data_to_dataset import \
    add_testcase_data_to_dataset


def load_json_data(data_path):
		with open(data_path, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return data["data"]


def create_math_explainer_data_set_for_ally(data_path):
	description = "Math_explainer_data_set"
	supabase_db = get_supabase_db()
	json_data = load_json_data(data_path)
	for data in tqdm(json_data):
		if "explanation" not in data:
				continue
		question = data["question"]
		choices = " ".join([choice for choice in data["choices"]])
		input_data = f"""
		This is the multiple choice math question:
		QUESTION: {question}
		CHOICES: {choices}
		"""
		response = supabase_db.create_testcase_data_from_message(
			description=description,
			input=input_data,
			reference_output=data["explanation"],
			context="no context provided",
		)
		add_testcase_data_to_dataset(
			dataset_id="9de57b38-6746-468e-8b6f-f111eeb70632",
			testcase_data_id=response.data[0]["testcase_data_id"],
		)
	print_text("Done")

if __name__ == "__main__":
	data_path = "examples/zalo_challenge/data/math_train.json"
	create_math_explainer_data_set_for_ally(data_path)
