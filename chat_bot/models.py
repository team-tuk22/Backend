from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
from google import generativeai as genai  # 제미나이 지원을 위한 임포트
from dotenv import load_dotenv  # 마찬가지.
import os

load_dotenv()

_HF_MODEL_NAME = "openai/gpt-oss-20b"
_hf_tokenizer: Optional[AutoTokenizer] = None
_hf_model: Optional[AutoModelForCausalLM] = None


_GEMINI_MODEL_NAME = "gemini-1.5-flash"
_gemini_client: Optional[genai.GenerativeModel] = None

def _ensure_huggingface_model_loaded() -> None:
    global _hf_tokenizer, _hf_model
    if _hf_tokenizer is None or _hf_model is None:
        _hf_tokenizer = AutoTokenizer.from_pretrained(_HF_MODEL_NAME)
        _hf_model = AutoModelForCausalLM.from_pretrained(
            _HF_MODEL_NAME,
            torch_dtype="auto",
            device_map="auto"
        )

def _ensure_gemini_model_loaded() -> None:
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("환경 변수에 API KEY가 없음. .env 파일에서 추가할 수 있음.")
        genai.configure(api_key=api_key)
        _gemini_client = genai.GenerativeModel(_GEMINI_MODEL_NAME)


def generate_response(
    user_message: str,
    db_results: Optional[List[Dict]] = None,
    # DB를 강력하게 참고하도록 프롬프트를 건드림.
    system_prompt: str = "당신은 법률 전문가이며, 오직 다음의 판례 데이터만을 참고하여 사용자 질문에 답변해야 합니다. 제공된 데이터에 없는 내용은 답변할 수 없습니다.",
    model_type: str = "huggingface",
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
):
    # 데이터베이스 결과를 콘솔에 출력함. 판례를 참고하는 게 맞는지 확인하는 작업.
    print("\n--- DB에서 검색된 판례 데이터 ---")
    print(db_results)
    print("------------------------------\n")

    full_user_message = user_message
    if db_results:
        result_str = "\n\n다음은 당신이 참고할 법률 판례 데이터입니다:\n"
        for i, item in enumerate(db_results):
            result_str += f"- 판례 {i+1}: 사건명: {item.get('title')}, 법원: {item.get('court')}, 선고일: {item.get('date')}, 상세 내용: {item.get('case_precedent')}\n"
        full_user_message += result_str
        
    if model_type == "gemini":
        _ensure_gemini_model_loaded()
        assert _gemini_client is not None

        full_prompt = f"{system_prompt}\n\nUser: {full_user_message}"
        response = _gemini_client.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_new_tokens
            )
        )
        return response.text
    elif model_type == "huggingface":
        _ensure_huggingface_model_loaded()
        assert _hf_tokenizer is not None and _hf_model is not None

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_message}
        ]

        input_text = _hf_tokenizer.apply_chat_template(messages)
        inputs = _hf_tokenizer(input_text, return_tensors="pt").to(_hf_model.device)
        outputs = _hf_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
        )
        result = _hf_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result
    else:
        return f"잘못된 모델 {model_type} 입니다. 'huggingface' 또는 'gemini'를 선택해주세요."