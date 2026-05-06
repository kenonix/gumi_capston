import litert_lm

# ========== 설정 파라미터 (임의로 조정 가능) ==========
# 모델 설정
MODEL_PATH = "/home/kenonix/다운로드/gemma-3n-E4B-it-int4.litertlm"
MAX_NUM_TOKENS = None          # 최대 토큰 수 (None: 제한 없음)
CACHE_DIR = ""                 # 캐시 디렉토리
ENABLE_SPECULATIVE_DECODING = None  # 예측적 디코딩 (None: 자동)

# 백엔드 설정
VISION_BACKEND = litert_lm.Backend.GPU
AUDIO_BACKEND = litert_lm.Backend.CPU

# 온도 및 생성 파라미터 (conversation 수준에서 사용)
TEMPERATURE = 0.7
TOP_K = 50
TOP_P = 0.95

#few-shot 참조 음성 샘플
REFERENCE_AUDIOS = [
    {"type": "audio", "path": "/home/kenonix/문서/오디오 파일/a1.wav", "context": "This is an example of a baby crying sound"},
    {"type": "audio", "path": "/home/kenonix/문서/오디오 파일/b1.wav", "context": "This is an example of footstep sounds"},
]

# 분류할 대상 음성
TARGET_AUDIO_PATH = "/home/kenonix/문서/오디오 파일/b1.wav"

# 프롬프트 텍스트
PROMPT_TEXT = "Separate the above voice from (baby crying) and (footballing). The output should be baby crying or footsteps depending on the voice properties. If it's not a sound, print None"

# ========== 메인 로직 ==========
litert_lm.set_min_log_severity(litert_lm.LogSeverity.ERROR)

with litert_lm.Engine(
    MODEL_PATH,
    max_num_tokens=MAX_NUM_TOKENS,
    cache_dir=CACHE_DIR,
    vision_backend=VISION_BACKEND,
    audio_backend=AUDIO_BACKEND,
    enable_speculative_decoding=ENABLE_SPECULATIVE_DECODING,
) as engine:
    with engine.create_conversation() as conversation:
        user_message = {
            "role": "user",
            "content": [
                # --- 참조 음성 샘플 (few-shot) ---
                *REFERENCE_AUDIOS,
                # --- 분류할 대상 음성 ---
                {"type": "audio", "path": TARGET_AUDIO_PATH},
                {"type": "text", "text": PROMPT_TEXT},
            ],
        }
        response = conversation.send_message(user_message)
        print(response["content"][0]["text"])
