

import os
import re
import logging
import requests
from flask import Blueprint, request, jsonify
from huggingface_hub import InferenceClient
from chat_db_utils import save_conversation_and_messages, get_conversations_by_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tinyllama_bp = Blueprint('tinyllama', __name__)

HF_TOKEN = os.environ.get("HF_TOKEN")
HF_MODEL_ID = "Sanjay002/tinyllama-mental-health-finetuned"

client = InferenceClient(
    provider="featherless-ai",
    api_key=HF_TOKEN,
)

def format_response(raw, prompt):
    cleaned = re.sub(r'<\|system\|>.*?</\|system\|>', '', raw, flags=re.DOTALL)
    cleaned = re.sub(r'<\|user\|>.*?</\|user\|>', '', cleaned, flags=re.DOTALL)
    cleaned = cleaned.replace('<|assistant|>', '').replace('</s>', '').replace('<s>', '')
    
    lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
    if lines and prompt.lower() in lines[0].lower():
        lines = lines[1:]
    
    return '\n'.join(lines).strip()

@tinyllama_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    logger.info(f"Received prompt from user {user_id}: {prompt[:50]}...")

    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        completion = client.chat.completions.create(
            model=HF_MODEL_ID,
            messages=messages,
            temperature=0.6,
            max_tokens=200,
        )
        generated_text = completion.choices[0].message["content"]
        output = format_response(generated_text, prompt)

        if user_id:
            conversation_id = save_conversation_and_messages(user_id, prompt, output, conversation_id)

        return jsonify({'response': output, 'conversation_id': conversation_id})

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({'response': f'Internal server error: {str(e)}'}), 500

@tinyllama_bp.route('/conversations', methods=['POST'])
def get_conversations():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'User not logged in.', 'conversations': []}), 401

    conversations = get_conversations_by_user(user_id)
    return jsonify({'conversations': conversations})
