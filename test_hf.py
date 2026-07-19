import os
import requests

hf_token = None
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('HF_TOKEN='):
            hf_token = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

url = "https://router.huggingface.co/hf-inference/models/distilbert-base-uncased-finetuned-sst-2-english"
headers = {"Authorization": f"Bearer {hf_token}"}
payload = {
    'inputs': "I love this!",
}

response = requests.post(url, headers=headers, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
