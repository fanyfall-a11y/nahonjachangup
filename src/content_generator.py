from google import genai as google_genai
import config

# 전역 클라이언트 변수 (싱글톤 패턴)
_client = None

def _get_client():
    """
    Google GenAI 클라이언트를 초기화하고 반환합니다.
    config.GEMINI_API_KEY가 없으면 None을 반환합니다.
    """
    global _client
    try:
        if _client is None and config.GEMINI_API_KEY:
            _client = google_genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as e:
        print(f"클라이언트 초기화 중 오류 발생: {e}")
        return None
    return _client

def generate_blog_post(program: dict, platform: str) -> str:
    """
    주어진 프로그램 정보를 바탕으로 블로그 포스팅 내용을 생성합니다.
    
    Args:
        program (dict): 사업 정보 딕셔너리 (title, agency, end_date 등)
        platform (str): 플랫폼 이름 (naver, tistory, blogspot 등)
        
    Returns:
        str: 생성된 블로그 포스팅 내용 또는 에러 메시지
    """
    try:
        client = _get_client()
        
        # 클라이언트가 초기화되지 않은 경우 처리
        if client is None:
            return "[Gemini API 키 미설정]"

        # 프로그램 정보 추출
        title = program.get("title", "")
        agency = program.get("agency", "")
        end_date = program.get("end_date", "")

        # 프롬프트 구성
        prompt = (
            f"나혼자창업 블로그 {platform} 포스팅 작성.\n"
            f"사업명: {title}\n"
            f"기관: {agency}\n"
            f"마감: {end_date}\n"
            "5단계 구조 필수:\n"
            "1.썸네일 타이틀\n"
            "2.사업목적/신청자격\n"
            "3.지원내용/신청방법\n"
            "4.신청기간/주관기관/문의처\n"
            "5.CTA: 구독과 좋아요는 큰 힘이 됩니다\n"
            f"{platform} SEO 최적화. 한국어."
        )

        # API 호출 (google-genai 패키지 방식)
        response = client.models.generate_content(
            model=config.GEMINI_MODEL, 
            contents=prompt
        )
        
        return response.text

    except Exception as e:
        print(f"블로그 포스팅 생성 중 오류 발생: {e}")
        return f"콘텐츠 생성 실패: {str(e)}"

def generate_instagram_caption(program: dict) -> str:
    """
    주어진 프로그램 정보를 바탕으로 인스타그램 멘트와 해시태그를 생성합니다.
    
    Args:
        program (dict): 사업 정보 딕셔너리
        
    Returns:
        str: 생성된 인스타그램 멘트 또는 기본 멘트
    """
    default_caption = (
        "혼자 창업하시는 분들을 위한 유용한 정보입니다! "
        "많은 관심과 참여 부탁드립니다. "
        "#나혼자창업 #정부지원사업 #창업지원"
    )

    try:
        client = _get_client()
        
        # 클라이언트가 없으면 기본 멘트 반환
        if client is None:
            return default_caption

        title = program.get("title", "")
        agency = program.get("agency", "")

        # 인스타그램용 프롬프트 구성
        prompt = (
            f"인스타그램 게시물용 멘트 작성.\n"
            f"사업명: {title}\n"
            f"기관: {agency}\n"
            "항상 응원합니다!\n"
            "해시태그: #나혼자창업 #정부지원사업 #창업지원 포함. "
            "감성적이고 짧은 문체로 작성. 한국어."
        )

        # API 호출
        response = client.models.generate_content(
            model=config.GEMINI_MODEL, 
            contents=prompt
        )
        
        return response.text

    except Exception as e:
        print(f"인스타그램 멘트 생성 중 오류 발생: {e}")
        # 에러 발생 시 기본 멘트 반환
        return default_caption

def generate_all_content(programs: list[dict]) -> dict:
    """
    여러 프로그램에 대해 모든 플랫폼의 콘텐츠를 생성하여 반환합니다.
    
    Args:
        programs (list[dict]): 사업 정보 리스트
        
    Returns:
        dict: 플랫폼별 생성된 콘텐츠 리스트 (naver, tistory, blogspot, instagram)
    """
    result = {
        "naver": [],
        "tistory": [],
        "blogspot": [],
        "instagram": []
    }

    try:
        # 프로그램 리스트가 비어있으면 빈 딕셔너리 반환
        if not programs:
            return {}

        # 설정된 개수만큼만 처리
        target_programs = programs[:config.CONTENT_LIMIT]

        for program in target_programs:
            # 블로그 포스팅 생성
            naver_post = generate_blog_post(program, "naver")
            tistory_post = generate_blog_post(program, "tistory")
            blogspot_post = generate_blog_post(program, "blogspot")

            # 인스타그램 멘트 생성
            insta_caption = generate_instagram_caption(program)

            # 결과 딕셔너리에 추가
            result["naver"].append(naver_post)
            result["tistory"].append(tistory_post)
            result["blogspot"].append(blogspot_post)
            result["instagram"].append(insta_caption)

    except Exception as e:
        print(f"전체 콘텐츠 생성 중 오류 발생: {e}")

    return result
