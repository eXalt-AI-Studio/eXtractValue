import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import json
from llm import call_llm

load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")

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
	return text, file_path

if __name__ == "__main__":
	
	data_folder = os.path.join(os.path.dirname(__file__), '../data')
	text, file_path = read_pdfs_in_folder(data_folder)
	print(f"Extracted text length: {len(text)} characters")
	print(f"Extracted file_path: {file_path} characters")
	print(f"Extracted text preview: {text}")

	SYSTEM_PROMPT = "You are a helpful assistant."

	with open("src/types/data-key.json", "r", encoding="utf-8") as f:
		json_schema = json.load(f)

	response, usage = call_llm(SYSTEM_PROMPT, "", file_path, json_schema, temperature=0.0)

	print("Response from LLM:")
	print(json.dumps(response, indent=2, ensure_ascii=False))