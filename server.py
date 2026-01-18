import uvicorn
import requests
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="TranslateGemma Service")

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "translategemma"
PORT = 8989

class TranslationRequest(BaseModel):
    text: str
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None

class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str

# Language definitions
LANG_MAP = {
    "zh": {"name": "Chinese (Traditional)", "code": "zh-TW"},
    "en": {"name": "English", "code": "en"},
    "ja": {"name": "Japanese", "code": "ja"},
}

def detect_language_strategy(text: str):
    """
    Heuristic to determine source and target language if not provided.
    Strategy:
    1. If text contains Japanese Kana -> Source: JA, Target: ZH
    2. If text contains Chinese chars -> Source: ZH, Target: EN
    3. Default -> Source: EN, Target: ZH
    """
    # Check for Hiragana or Katakana (Japanese specific)
    if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
        return "ja", "zh"
    
    # Check for Common CJK Unified Ideographs (Chinese/Kanji)
    # Since we ruled out pure Kana above, if this exists it's likely Chinese source
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh", "en"
        
    # Default assumption
    return "en", "zh"

def get_lang_details(code: str):
    return LANG_MAP.get(code, {"name": code, "code": code})

def construct_prompt(source_code, target_code, text):
    src = get_lang_details(source_code)
    tgt = get_lang_details(target_code)
    
    prompt = (
        f"You are a professional {src['name']} ({src['code']}) to {tgt['name']} ({tgt['code']}) translator. "
        f"Your goal is to accurately convey the meaning and nuances of the original {src['name']} text "
        f"while adhering to {tgt['name']} grammar, vocabulary, and cultural sensitivities. "
        f"Produce only the {tgt['name']} translation, without any additional explanations or commentary.\n\n"
        f"Please translate the following {src['name']} text into {tgt['name']}:\n"
        f"{text}"
    )
    return prompt

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    # Auto-detect if not specified
    if not request.source_lang or not request.target_lang:
        detected_src, detected_tgt = detect_language_strategy(request.text)
        src_lang = request.source_lang or detected_src
        tgt_lang = request.target_lang or detected_tgt
    else:
        src_lang = request.source_lang
        tgt_lang = request.target_lang

    prompt = construct_prompt(src_lang, tgt_lang, request.text)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3 # Lower temperature for more deterministic translation
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        translated_text = result.get("response", "").strip()
        
        return TranslationResponse(
            translated_text=translated_text,
            source_lang=src_lang,
            target_lang=tgt_lang
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Ollama connection failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Access log disabled for cleaner background run, only errors shown
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="error")
