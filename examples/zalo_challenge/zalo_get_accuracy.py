import csv
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

if __name__ == '__main__':
	parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
	parser.add_argument("-f", "--file", default="", help="result file to calculate accuracy")
	parser.add_argument("-m", "--match", default="exact", help="type of match to calculate accuracy")
	args = parser.parse_args()
	file = args.file
	match = args.match
	# read the csv file and calculate accuracy based on prediction and answer fields
	with open(file, 'r', encoding='utf-8') as f:
		reader = csv.DictReader(f)
		total = 0
		correct = 0
		for row in reader:
			total += 1
			if match == "exact":
				# remove all the extra spaces
				prediction = row["prediction"].strip()
				answer = row["answer"].strip()
				if prediction == answer:
					correct += 1
			else:
				raise ValueError(f"Unsupported match type: {match}")
		print(f"Total: {total}, correct: {correct}, accuracy: {correct/total}")