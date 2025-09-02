from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM


_MODEL_NAME = "openai/gpt-oss-20b"
_tokenizer: Optional[AutoTokenizer] = None
_model: Optional[AutoModelForCausalLM] = None


def _ensure_model_loaded() -> None:
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(
            _MODEL_NAME,
            torch_dtype="auto",
            device_map="auto"
        )


def generate_response(
    user_message: str,
    system_prompt: str = "You are a helpful assistant.",
    max_new_tokens: int = 256,
    temperature: float = 0.7,
) -> str:
    _ensure_model_loaded()
    assert _tokenizer is not None and _model is not None

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    input_text = _tokenizer.apply_chat_template(messages)
    inputs = _tokenizer(input_text, return_tensors="pt").to(_model.device)
    outputs = _model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True,
    )
    result = _tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result