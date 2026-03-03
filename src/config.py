import os

# === 공공데이터 API ===
BIZINFO_API_KEY = os.environ.get("BIZINFO_API_KEY", "")  # 기업마당 API 인증키
KSTARTUP_API_KEY = os.environ.get("KSTARTUP_API_KEY", "")  # 공공데이터포털 K-Startup 서비스키

# === Gemini API ===
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")  # Google AI Studio API 키
GEMINI_MODEL = "gemini-1.5-pro"  # 사용할 Gemini 모델명

# === 이메일 (Gmail SMTP) ===
EMAIL_FROM = os.environ.get("EMAIL_FROM", "")  # 발신 Gmail 주소
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")  # Gmail 앱 비밀번호
EMAIL_TO_RAW = os.environ.get("EMAIL_TO", "")  # 수신자 (콤마 구분 문자열)
EMAIL_TO = [e.strip() for e in EMAIL_TO_RAW.split(",") if e.strip()]  # 수신자 리스트

# === 브랜드 설정 ===
BRAND_NAME = "나혼자창업"  # 브랜드명
BRAND_COLOR_PRIMARY = (30, 90, 180)  # Trust Blue RGB
BRAND_COLOR_SECONDARY = (255, 255, 255)  # 흰색
BLOG_PLATFORMS = ["naver", "tistory", "blogspot"]  # 지원 블로그 플랫폼

# === 이미지 설정 ===
IMAGE_DIR = "output/images/"  # 카드뉴스 저장 경로
IMAGE_WIDTH = 1080  # 인스타그램 카드 너비 (px)
IMAGE_HEIGHT = 1620  # 인스타그램 카드 높이 (px, 2:3 비율)
IMAGE_CARDS_COUNT = 5  # 카드뉴스 장수
CONTENT_LIMIT = 3  # 콘텐츠 생성 대상 사업 수

# === 스케줄 / 로그 ===
SCHEDULE_TIME = "09:10"  # 자동 실행 시각 (KST)
LOG_DIR = "logs/"  # 로그 파일 저장 경로
LOG_RETENTION_DAYS = 30  # 로그 보관 기간 (일)

# === 수집 설정 ===
OUTPUT_DIR = "output/"  # 결과 저장 경로
OUTPUT_FORMAT = "json"  # 저장 형식: json 또는 markdown
MAX_PAGES = 5  # API 최대 페이지 수
ROWS_PER_PAGE = 20  # 페이지당 항목 수
REQUEST_TIMEOUT = 10  # HTTP 타임아웃(초)
REQUEST_DELAY = 0.5  # 요청 간 딜레이(초)
FILTER_KEYWORDS = ["스타트업", "창업", "중소기업", "벤처", "청년"]  # 사업명 필터 키워드
FILTER_FIELDS = ["창업", "기술", "금융", "인력", "수출"]  # 지원분야 필터
CRAWL_FALLBACK = True  # API 장애 시 크롤링 보완 여부
DEADLINE_DAYS_AHEAD = 30  # 마감일 필터 기준(일)
URGENT_DAYS = 7  # 마감임박 기준(일)
