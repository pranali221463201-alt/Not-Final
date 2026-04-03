import torch
from .model_loader import load_model

# Lazy load model (singleton behavior)
_model_cache = None
_tokenizer_cache = None
_id_to_label_cache = None
_device_cache = None

def _get_model():
    """Lazy load model on first use"""
    global _model_cache, _tokenizer_cache, _id_to_label_cache, _device_cache
    
    if _model_cache is None:
        try:
            _tokenizer_cache, _model_cache, _id_to_label_cache, _device_cache = load_model()
        except Exception as e:
            print(f"Warning: Could not load plastic risk model: {e}")
            return None, None, None, None
    
    return _tokenizer_cache, _model_cache, _id_to_label_cache, _device_cache

def predict_inherent_risk(text: str) -> dict:
    """
    Pure ML inference.
    No DB, no rules, no side effects.
    """
    
    tokenizer, model, id_to_label, device = _get_model()
    
    if model is None:
        return {
            "category": "Unknown",
            "confidence": 0.0,
            "error": "Model not available"
        }

    if not text or not isinstance(text, str):
        return {
            "category": "Unknown",
            "confidence": 0.0
        }

    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)

    pred_id = torch.argmax(probs, dim=1).item()

    return {
        "category": id_to_label[pred_id],
        "confidence": round(probs[0][pred_id].item(), 4)
    }
