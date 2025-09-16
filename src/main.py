import csv
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import json
from llm import call_llm
from llm_text import call_llm_text

load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")

def save_json_to_csv(data, filename):
	"""Save JSON data (dict or list of dicts) to a CSV file."""
	if isinstance(data, dict):
		data = [data]
	if not data:
		return
	file_exists = os.path.isfile(filename)
	with open(filename, "a", encoding="utf-8", newline="") as f:
		writer = csv.DictWriter(f, fieldnames=data[0].keys())
		if not file_exists or os.stat(filename).st_size == 0:
			writer.writeheader()
		writer.writerows(data)

def extract_key_data_with_text(text):
	"""Extract key data from text using the LLM."""
	with open("src/types/data-key.json", "r", encoding="utf-8") as f:
		json_schema = json.load(f)
	response, usage = call_llm_text("You are a helpful assistant.", "", text, json_schema, temperature=0.0)
	print("Response from LLM with text:")
	print(json.dumps(response, indent=2, ensure_ascii=False))
	save_json_to_csv(response, "output/output_text.csv")
	return response, usage

def extract_key_data_with_pdf(file_path):
	"""Extract key data from a PDF file using the LLM."""
	with open("src/types/data-key.json", "r", encoding="utf-8") as f:
		json_schema = json.load(f)
	response, usage = call_llm("You are a helpful assistant.", "", file_path, json_schema, temperature=0.0)
	print("Response from LLM with PDF:")
	print(json.dumps(response, indent=2, ensure_ascii=False))
	save_json_to_csv(response, "output/output_pdf.csv")
	return response, usage

def read_pdfs_in_folder(folder):
	"""Browse all files in the folder and read PDF files."""
	for filename in os.listdir(folder):
		file_path = os.path.join(folder, filename)
		if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
			print(f"Reading file: {filename}")
			try:
				reader = PdfReader(file_path)
				text = ""
				for page in reader.pages:
					text += page.extract_text() or ""
			except Exception as e:
				print(f"Error reading {filename}: {e}")
			extract_key_data_with_pdf(file_path)
			extract_key_data_with_text(text)
	return text, file_path

if __name__ == "__main__":
	
	data_folder = os.path.join(os.path.dirname(__file__), '../data')
	text, file_path = read_pdfs_in_folder(data_folder)

