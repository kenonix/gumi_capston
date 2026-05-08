from openai import OpenAI
import json
import base64

# =========================================
# 설정
# =========================================
# OpenAI API 키 설정
API_KEY = "b4IxBUBRiIkzStnhqJN4gyWCViPLiohq"

# OpenAI 클라이언트 초기화 (FactChat 게이트웨이 사용)
client = OpenAI(
    api_key=API_KEY,
    base_url="https://factchat-cloud.mindlogic.ai/v1/gateway",
)

# =========================================
# 오디오 파일 읽어서 base64 인코딩
# =========================================
# 분석할 음성 파일 경로 설정
audio_file_path = r"c:\Users\drone\OneDrive\바탕 화면\b1.mp3"

# 음성 파일을 읽고 base64로 인코딩 (API 전송을 위함)
with open(audio_file_path, "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode("utf-8")

# =========================================
# Chat Completion 요청
# =========================================
# Gemini 2.5 Flash 모델을 사용하여 음성 분석 요청
# 요청 내용: 음성 파일에서 아기 울음소리 또는 발소리 구분
response = client.chat.completions.create(
    model="gemini-2.5-flash",  # 음성 입력을 지원하는 모델
    messages=[
        {
            "role": "user",  # 사용자의 요청
            "content": [
                {
                    "type": "text",
                    "text": "이 음성을 듣고 아기 울음소리, 발소리 중에서 어떤 소리인지 구분해줘. 만약 둘 다 아니라면 None이라고 답변해줘."
                },
                {
                    "type": "input_audio",  # 음성 파일 입력
                    "input_audio": {
                        "data": audio_base64,  # Base64로 인코딩된 음성 데이터
                        "format": "mp3"  # MP3 포맷
                    }
                }
            ]
        }
    ],
    temperature=0.2,  # 창의성 수준 (낮을수록 더 일관된 결과)