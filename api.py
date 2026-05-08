from openai import OpenAI
import json
import base64

# =========================================
# 설정
# =========================================
API_KEY = "b4IxBUBRiIkzStnhqJN4gyWCViPLiohq"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://factchat-cloud.mindlogic.ai/v1/gateway",
)

# =========================================
# 오디오 파일 읽어서 base64 인코딩
# =========================================
audio_file_path = r"c:\Users\drone\OneDrive\바탕 화면\b1.mp3"

with open(audio_file_path, "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode("utf-8")

# =========================================
# Chat Completion 요청
# =========================================
response = client.chat.completions.create(
    model="gemini-2.5-flash",  # audio input 지원 모델 사용 권장
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "이 음성을 듣고 아기 울음소리, 발소리 중에서 어떤 소리인지 구분해줘. 만약 둘 다 아니라면 None이라고 답변해줘."
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_base64,
                        "format": "mp3"  # mp3면 "mp3"
                    }
                }
            ]
        }
    ],
    temperature=0.2,
)