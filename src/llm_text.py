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

def call_llm_text(
    system_prompt: str,
    user_message: str,
    text: str,
    json_schema: Dict,
    model: str = "google/gemini-2.5-pro",
    temperature: float = 0.0,
) -> Tuple[Dict, Dict]:
    """Send a chat request with an attached text and return the JSON response with usage."""

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
                {"type": "text", "text": text},
            ],
        },
    ]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        'provider': {
        'require_parameters': True
        },
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "key-data",
                "strict": True,
                "description": "Extracts key data from the lease agreement.",
                "schema": json_schema,
            },
        },
        "temperature": temperature,
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
    )

    resp = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"LLM request failed: {resp}")

    content = resp["choices"][0]["message"]["content"]
    json_response = json.loads(content)
    usage = resp.get("usage", {})
    return json_response, usage
