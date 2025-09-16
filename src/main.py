import os
from PyPDF2 import PdfReader

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
	return text

if __name__ == "__main__":
	data_folder = os.path.join(os.path.dirname(__file__), '../data')
	text = read_pdfs_in_folder(data_folder)
	print(f"Extracted text length: {len(text)} characters")
	print(f"Extracted text preview: {text}")
