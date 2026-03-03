import sys
import requests
import json

# --- [설정 확인] ---
# 1. Z.ai 대시보드에서 복사한 API 키를 아래 따옴표 안에 넣으세요.
GLM_API_KEY = "1cddd09248a446c1b3a321e362a0eda3.qjKNDivpLIYVG0uC" 

# 2. Z.ai V4 엔드포인트 주소입니다.
BASE_URL = "https://api.z.ai/api/coding/paas/v4/chat/completions" 

# 3. 효율적인 개발을 위해 GLM-4.7 모델을 사용합니다.
MODEL_NAME = "glm-4.7" 
# ------------------

def ask_glm(prompt):
    headers = {
        "Authorization": f"Bearer {GLM_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "너는 코딩 전문 비서야. 불필요한 설명 없이 코드 결과물만 출력해."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(BASE_URL, json=data, headers=headers, timeout=60)
        
        # 성공(200)이 아닐 경우 서버의 상세 에러 메시지를 출력합니다.
        if response.status_code != 200:
            print(f"\n❌ [서버 응답 에러 {response.status_code}]")
            print(f"상세 이유: {response.text}")
            return "연결 실패"
        
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"실행 중 오류 발생: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 터미널 입력을 처리하여 결과를 출력합니다.
        result = ask_glm(sys.argv[1])
        print(result)