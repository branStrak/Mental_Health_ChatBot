

import os
import re
import logging
import requests
from flask import Blueprint, request, jsonify
from chat_db_utils import save_conversation_and_messages, get_conversations_by_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tinyllama_bp = Blueprint('tinyllama', __name__)

HF_TOKEN = os.environ.get("HF_TOKEN", "your_hf_token_here")  # Replace with your actual token
HF_MODEL_ID = "Sanjay002/tinyllama-mental-health-finetuned"
API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def format_response(raw, prompt):
    raw = re.sub(r"<\|?assistant\|?>:?", "", raw, flags=re.IGNORECASE)
    if raw.strip().startswith(prompt.strip()):
        raw = raw[len(prompt):].strip()
    raw = re.sub(r"\n\s*\d+\.", "\n\n•", raw)
    raw = re.sub(r"\n\s*-\s*", "\n\n•", raw)
    raw = re.sub(r"\n{2,}", "\n\n", raw.strip())
    if raw and raw[0].islower():
        raw = raw[0].upper() + raw[1:]
    if raw and not raw.endswith(('.', '!', '?')):
        sentences = re.split(r'([.!?])', raw)
        complete = ''
        for i in range(0, len(sentences) - 1, 2):
            complete += sentences[i] + sentences[i + 1]
        raw = complete.strip() if complete else raw
    if raw and not raw.endswith("💛"):
        raw += "\n\nYou're not alone — small steps matter. 💛"
    return raw

@tinyllama_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        user_id = data.get('user_id')

        if not prompt:
            return jsonify({'response': 'Prompt is missing.'}), 400

        response = requests.post(API_URL, headers=headers, json={
            'inputs': prompt,
            'parameters': {
                'max_new_tokens': 200,
                'temperature': 0.6,
                'top_p': 0.9,
                'repetition_penalty': 1.2
            }
        })

        if response.status_code == 200:
            try:
                result = response.json()
                generated_text = result[0]['generated_text']
                output = format_response(generated_text, prompt)
            except Exception as e:
                logger.error(f"⚠️ Error parsing JSON: {e}")
                output = "AI responded, but couldn't be parsed."
        else:
            logger.error(f"❌ HF API Error [{response.status_code}]: {response.text}")
            output = "The AI is not available right now. Please try again shortly."

        conversation_id = None
        if user_id:
            conversation_id = save_conversation_and_messages(user_id, prompt, output)

        return jsonify({'response': output, 'conversation_id': conversation_id})

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({'response': 'Internal server error.'}), 500

@tinyllama_bp.route('/conversations', methods=['POST'])
def get_conversations():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'User not logged in.', 'conversations': []}), 401

    conversations = get_conversations_by_user(user_id)
    return jsonify({'conversations': conversations})
