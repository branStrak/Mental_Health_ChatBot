from flask import Blueprint, request, jsonify
from huggingface_hub import InferenceClient
from chat_db_utils import save_conversation_and_messages
import re

gemma_bp = Blueprint('gemma', __name__)

import re

def clean_response(response_text):
    raw = response_text.strip()

    # Fix sentence fragments that may not end with proper punctuation
    if raw and not raw.endswith(('.', '!', '?')):
        sentences = re.split(r'([.!?])', raw)
        complete = ''
        for i in range(0, len(sentences) - 1, 2):
            complete += sentences[i] + sentences[i + 1]
        raw = complete.strip() if complete else raw

    cleaned_text = raw.replace("**", "").replace("* ", "- ").replace("#", "").replace("- -", "-")

    # Ensure clean line splitting
    lines = cleaned_text.split("\n")
    formatted_lines = []
    current_section = None

    section_header_pattern = re.compile(r'^\d+\.\s|^[-•]?\s?[A-Z][^:]*:$')  # Handles "1. Emotional..." or "Some Title:"

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect section headers like "1. Emotional Well-being:" or "Social Well-being:"
        if section_header_pattern.match(line):
            current_section = line.rstrip(":")
            formatted_lines.append(f"\n{current_section}:")
        else:
            # Normalize double bullets or inconsistent formatting
            bullet_line = re.sub(r'^[-•]?\s*', '- ', line)
            formatted_lines.append(f"  {bullet_line}")

    # Join all formatted lines
    cleaned_output = "\n".join(formatted_lines).strip()
    print(cleaned_output)
    return cleaned_output

import os
from huggingface_hub import InferenceClient

hf_token = os.environ.get("HF_TOKEN")
client = InferenceClient(
    provider="Featherless AI",
    api_key=hf_token,
)

@gemma_bp.route('', methods=['POST']) 
def chat_grok():
    data = request.get_json()
    prompt = data.get('prompt')
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id') 

    print("📩 Received user_id:", user_id, "| conversation_id:", conversation_id)

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    messages = [
        {"role": "user", "content": prompt}
    ]

    try:
        completion = client.chat.completions.create(
            model="google/gemma-2-2b-it",
            messages=messages,
            temperature=0.7,
            max_tokens=350,
        )
        raw_response = completion.choices[0].message["content"]
        cleaned_response = clean_response(raw_response)

        updated_convo_id = None
        if user_id:
            updated_convo_id = save_conversation_and_messages(user_id, prompt, cleaned_response, conversation_id) 

        return jsonify({'response': cleaned_response, 'conversation_id': updated_convo_id}) 
    except Exception as e:
        return jsonify({'response': f'Failed to get response from model: {str(e)}'}), 500

