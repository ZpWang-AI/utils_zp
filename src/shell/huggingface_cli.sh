# pip install -U "huggingface_hub[cli]"

export HF_ENDPOINT="https://hf-mirror.com"

huggingface-cli download FacebookAI/roberta-base \
    --local-dir ~/pretrained_models/roberta-base
