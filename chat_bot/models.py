from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
from google import generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# 허깅페이스, 제미나이 모델에 대한 변수 설정.
HF_MODEL_NAME = "openai/gpt-oss-20b"
hf_tokenizer: Optional[AutoTokenizer] = None
hf_model: Optional[AutoModelForCausalLM] = None

GEMINI_MODEL_NAME = "gemini-2.5-flash"
gemini_client: Optional[genai.GenerativeModel] = None


# 허깅페이스 모델(OPENAI) 로드
def _load_hf_model() -> None:
    global hf_tokenizer, hf_model
    if hf_tokenizer is None or hf_model is None:
        hf_tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
        hf_model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL_NAME,
            torch_dtype="auto",
            device_map="auto"
        )

# 제미나이 모델 로드
def _load_gemini_model() -> None:
    global gemini_client
    if gemini_client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("환경 변수 GOOGLE_API_KEY가 없음. .env 파일에서 추가하세요.")
        genai.configure(api_key=api_key)
        gemini_client = genai.GenerativeModel(GEMINI_MODEL_NAME)


def make_response(
    user_q: str,  # 사용자의 실제 질문
    db_data: Optional[List[Dict]] = None,  # DB 검색으로 얻은 판례 데이터
    system_prompt: str = "당신은 법률 전문가이며, 오직 다음의 판례 데이터만을 참고하여 사용자 질문에 답변해야 합니다. 제공된 데이터에 없는 내용은 답변할 수 없습니다.",
    model_type: str = "huggingface",  # 사용할 AI 모델 타입 ('huggingface' 또는 'gemini')
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
):
    # 디버깅 목적. AI 모델이 제대로 DB를 넘겨받았는지 확인하기 위한 용도임. 
    print("\n--- DB에서 검색된 판례 데이터 ---")
    print(db_data)
    print("-FIN-\n")
    # 여기까지가 디버깅 용도 코드.

    # 사용자 질문과 DB 결과를 합쳐서 AI에게 전달할 전체 메시지 생성
    full_message = user_q
    if db_data:
        db_text = "\n\n다음은 당신이 참고할 법률 판례 데이터입니다:\n"
        for i, item in enumerate(db_data):
            db_text += f"- 판례 {i+1}: 사건명: {item.get('title')}, 법원: {item.get('court')}, 선고일: {item.get('date')}, 상세 내용: {item.get('case_precedent')}\n"
        full_message += db_text
        
    # 모델 타입에 따라 다른 AI 모델 API 호출
    if model_type == "gemini":
        _load_gemini_model()  # 제미나이 모델 로드
        assert gemini_client is not None

        # 프롬프트 구성 및 제미나이 API 호출
        full_prompt = f"{system_prompt}\n\nUser: {full_message}"
        response = gemini_client.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_new_tokens
            )
        )
        return response.text
    elif model_type == "huggingface":
        _load_hf_model()  # 허깅페이스 모델 로드
        assert hf_tokenizer is not None and hf_model is not None

        # 대화 템플릿에 맞게 메시지 구성
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_message}
        ]

        # 텍스트를 토큰으로 변환하고 모델에 전달
        input_ids = hf_tokenizer.apply_chat_template(messages, return_tensors="pt").to(hf_model.device)
        output = hf_model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
        )
        # 생성된 토큰을 다시 텍스트로 변환하여 반환
        result = hf_tokenizer.decode(output[0], skip_special_tokens=True)
        return result
    else:
        return f"잘못된 모델 {model_type}. 'huggingface' 또는 'gemini'를 선택해주세요."