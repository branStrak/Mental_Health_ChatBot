from huggingface_hub import HfApi

api = HfApi()
models = api.list_models(limit=20, filter="text-generation-inference")
for m in models:
    print(m.modelId)
