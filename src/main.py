import csv
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import json
from llm import call_llm
from llm_text import call_llm_text
from llm_ocr import call_llm_ocr
from PyPDF2 import PdfWriter
import io
from tesseract_s3 import extract_plain_text_from_pdf_async

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

def extract_key_data_with_text(file, text):
	"""Extract key data from text using the LLM."""
	with open("src/types/data-key.json", "r", encoding="utf-8") as f:
		json_schema = json.load(f)
	response, usage = call_llm_text("You are a helpful assistant.", "", text, json_schema, temperature=0.0)
	if isinstance(response, dict):
		response['filename'] = file
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

def read_pdfs_in_s3(file):
	"""Browse pdf files in the S3 folder and extract text using OCR."""
	base_name = os.path.splitext(os.path.basename(file))[0]
	output_txt_path = os.path.join("output", f"{base_name}.txt")

	if os.path.exists(output_txt_path):
		with open(output_txt_path, "r", encoding="utf-8") as txt_file:
			text_ocr = txt_file.read()
	else:
		text_ocr = extract_plain_text_from_pdf_async(file)
		with open(output_txt_path, "w", encoding="utf-8") as txt_file:
			txt_file.write(text_ocr)
	extract_key_data_with_text(file, text_ocr)
	print(f"OCR Text from {file}: {len(text_ocr)}")
	return file

if __name__ == "__main__":
	list_files = ["fayet_bail_commercial.pdf",
			   "Q448 ANTIBES - 0707 Bail_biff.pdf",
			   "bail type SLB - Foncire Des Murs - 29 mai 2007_biff.pdf",
			   "cong + bail VILLEPINTE FQ 1er tage_biff.pdf",
			   "cong + bail VILLEPINTE FQ 2me tage_biff.pdf",
			   "cong + bail VILLEPINTE QR 1er tage_biff.pdf",
			   "Q145 CREIL - 0909 LGAI_biff.pdf",
			   "Q153 FAYET - 1002 LGAI_biff.pdf",
			   "Q241 BESANCON CHATEAUFARINE - 0709 ssbail commercial_biff.pdf",
			   "Bail FQ - Saint Etienne_biff.pdf",
			   "bail LA PLAINE_biff.pdf"]
	for file in list_files:
		file_path = read_pdfs_in_s3(file)