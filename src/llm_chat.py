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

def call_llm_chat(
    system_prompt: str,
    user_message: str,
    text: str,
    model: str = "google/gemini-2.5-flash_lite",
    temperature: float = 0.0,
    stream: bool = False,
):
    """Send a chat request with an attached text and return the JSON response with usage. If stream=True, yield tokens as they arrive."""

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
        "temperature": temperature,
        "stream": stream,
    }

    if stream:
        with requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
        ) as response:
            if response.status_code != 200:
                try:
                    resp = response.json()
                except Exception:
                    resp = response.text
                raise RuntimeError(f"LLM request failed: {resp}")
            for line in response.iter_lines(decode_unicode=False):
                if isinstance(line, bytes):
                    line = line.decode("utf-8", errors="replace")
                if line and line.startswith("data: "):
                    data = line[len("data: "):]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue
    else:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        resp = response.json()
        if response.status_code != 200:
            raise RuntimeError(f"LLM request failed: {resp}")
        json_response = resp["choices"][0]["message"]["content"]
        usage = resp.get("usage", {})
        return json_response, usage
