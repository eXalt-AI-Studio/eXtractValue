import base64
import json
import os
from typing import Dict, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")


def _encode_pdf_to_base64(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def call_llm_ocr(
    pdf_path: str,
    model: str = "google/gemini-2.5-pro",
) -> Tuple[Dict, Dict]:
    """Send a chat request with an attached PDF and return the JSON response with usage."""

    base64_pdf = _encode_pdf_to_base64(pdf_path)
    data_url = f"data:application/pdf;base64,{base64_pdf}"

    messages = [
        {
            "role": "system", 
            "content": "You are an OCR assistant. Extract and return only the raw text content from the provided PDF file, without any formatting or interpretation."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text":  "Please extract the plain text from this PDF."
                },
                {
                    "type": "file",
                    "file": {
                        "filename": os.path.basename(pdf_path),
                        "file_data": data_url,
                    },
                },
            ],
        },
    ]

    plugins = [
        {
            "id": "file-parser",
            "pdf": {
                "engine": "pdf-text"
            }
        }
    ]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "plugins": plugins
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    try:
        resp = response.json()
    except Exception as e:
        print("Error decoding JSON response:", e)
        print("Raw response text:\n", response.text)
        raise RuntimeError(f"LLM request failed: Could not decode JSON. Raw response: {response.text}")
    if response.status_code != 200:
        raise RuntimeError(f"LLM request failed: {resp}")

    content = resp["choices"][0]["message"]["content"]
    json_response = json.loads(content)
    usage = resp.get("usage", {})

    return json_response, usage
