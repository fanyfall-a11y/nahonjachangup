from datetime import datetime

def print_summary(total_raw: int, total_filtered: int, urgent_count: int) -> None:
    """
    오늘 날짜와 함께 수집 건수 요약을 출력하는 함수입니다.
    """
    try:
        # 오늘 날짜 포맷팅 (YYYY-MM-DD)
        today = datetime.now().strftime("%Y-%m-%d")
        
        print("=" * 40)
        print(f"[정부지원사업 안내] {today} 기준")
        print(f"총 수집: {total_raw}건 | 필터 후: {total_filtered}건 | 마감임박: {urgent_count}건")
        print("=" * 40)
    except Exception as e:
        # 날짜 처리나 출력 중 오류 발생 시 처리
        print(f"[오류] 요약 정보 출력 중 문제가 발생했습니다: {e}")

def print_urgent_alert(programs: list[dict]) -> None:
    """
    상태가 '마감임박'인 항목만 출력하는 함수입니다.
    """
    try:
        # 상태가 '마감임박'인 항목 필터링
        urgent_programs = [p for p in programs if p.get("status") == "마감임박"]
        
        if not urgent_programs:
            print("마감임박 공고 없음")
            return
        
        for idx, prog in enumerate(urgent_programs, 1):
            title = prog.get("title", "알 수 없음")
            agency = prog.get("agency", "알 수 없음")
            end_date = prog.get("end_date", "알 수 없음")
            
            # [N] 사업명 | 기관명 | 마감: YYYY-MM-DD 형식 출력
            print(f"[{idx}] {title} | {agency} | 마감: {end_date}")
            
    except Exception as e:
        print(f"[오류] 마감임박 알림 출력 중 문제가 발생했습니다: {e}")

def print_program_list(programs: list[dict]) -> None:
    """
    전체 사업 목록을 출력하는 함수입니다.
    """
    try:
        if not programs:
            print("출력할 공고 목록이 없습니다.")
            return

        for idx, prog in enumerate(programs, 1):
            title = prog.get("title", "알 수 없음")
            agency = prog.get("agency", "알 수 없음")
            field = prog.get("field", "알 수 없음")
            end_date = prog.get("end_date", "알 수 없음")
            status = prog.get("status", "알 수 없음")
            detail_url = prog.get("detail_url", "")
            
            # 지정된 형식으로 출력
            print(f"[{idx}] {title}")
            print(f"    기관: {agency} | 분야: {field} | 마감: {end_date} | 상태: [{status}]")
            print(f"    URL: {detail_url}")
            
    except Exception as e:
        print(f"[오류] 사업 목록 출력 중 문제가 발생했습니다: {e}")

def print_error(message: str) -> None:
    """
    [오류] 접두사가 붙은 메시지를 출력하는 함수입니다.
    """
    try:
        print(f"[오류] {message}")
    except Exception:
        # 오류 출력 함수 자체의 예외는 무시 (혹은 stderr로 출력 등)
        pass
