import os
from huggingface_hub import InferenceClient

hf_token = None
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('HF_TOKEN='):
            hf_token = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

print("Using token:", hf_token[:10] + "...")

client = InferenceClient(api_key=hf_token, provider="together")
try:
    print("Sending request...")
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",
        messages=[{"role": "system", "content": "You are a mental health bot."}, {"role": "user", "content": "I feel sad."}],
        max_tokens=20
    )
    print("Success:", response)
except Exception as e:
    print("Error:", repr(e))
