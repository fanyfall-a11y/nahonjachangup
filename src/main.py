import sys
import os
import time
from datetime import datetime

# 로컬 모듈 import를 위한 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_client import fetch_all_api_programs
from crawler import crawl_all_fallback
from data_processor import run_pipeline
import notifier
import storage
import logger
import content_generator
import image_generator
import mailer

def main() -> None:
    """
    나혼자창업 자동화 시스템 전체 파이프라인 오케스트레이터
    """
    # 1. 시작 시간 기록
    start_time = time.time()

    # 2. 실행 로그 시작 기록
    logger.log_run_start()

    # 3. 시작 메시지 출력
    print("=== 나혼자창업 지원사업 수집 시작 ===")

    # 수집 데이터 초기화
    raw_api = []
    raw_crawl = []
    raw_programs = []

    # 4. API 프로그램 수집
    try:
        raw_api = fetch_all_api_programs()
    except Exception as e:
        print(f"[오류] API 수집 실패: {e}")

    # 5. 크롤러 대체 수집
    try:
        raw_crawl = crawl_all_fallback()
    except Exception as e:
        print(f"[오류] 크롤링 수집 실패: {e}")

    # 6. 원시 데이터 병합
    raw_programs = raw_api + raw_crawl

    # 처리된 데이터 초기화
    processed = []

    # 7. 데이터 파이프라인 처리
    try:
        processed = run_pipeline(raw_programs)
    except Exception as e:
        print(f"[오류] 데이터 파이프라인 처리 실패: {e}")

    # 8. 마감임박 건수 계산
    urgent_count = 0
    if processed:
        urgent_count = len([p for p in processed if p.get("status") == "마감임박"])

    # 9. 요약 출력
    notifier.print_summary(len(raw_programs), len(processed), urgent_count)

    # 10. 긴급 알림 출력
    notifier.print_urgent_alert(processed)

    # 11. 전체 목록 출력
    notifier.print_program_list(processed)

    # 저장 경로 초기화
    saved_path = ""

    # 12. 결과 저장
    try:
        saved_path = storage.save(processed)
    except Exception as e:
        print(f"[오류] 저장 실패: {e}")

    # 13. 실행 결과 로깅
    try:
        logger.log_run_result(len(raw_programs), len(processed), urgent_count, saved_path)
    except Exception as e:
        print(f"[오류] 결과 로깅 실패: {e}")

    # 콘텐츠 초기화
    content = {}

    # 14. 콘텐츠 생성 (데이터가 있을 경우)
    if processed:
        try:
            content = content_generator.generate_all_content(processed)
        except Exception as e:
            print(f"[오류] 콘텐츠 생성 실패: {e}")

    # 14-2. 콘텐츠 파일 저장 (멘트요약 / 블로그 글)
    if processed and content:
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            storage.save_content_files(processed[:config.CONTENT_LIMIT], content, today_str)
        except Exception as e:
            print(f"[오류] 콘텐츠 파일 저장 실패: {e}")

    # 이미지 경로 초기화
    image_paths = []

    # 15. 카드뉴스 이미지 생성 (데이터가 있을 경우)
    if processed:
        today_str = datetime.now().strftime("%Y-%m-%d")
        try:
            image_paths = image_generator.create_card_set(processed[0], today_str)
        except Exception as e:
            print(f"[오류] 이미지 생성 실패: {e}")

    # 16. 이메일 발송
    try:
        mailer.send_daily_report(processed, content, image_paths)
    except Exception as e:
        print(f"[오류] 이메일 발송 실패: {e}")

    # 17. 소요 시간 계산
    elapsed = time.time() - start_time

    # 18. 종료 메시지 출력
    print(f"=== 수집 완료 | 소요 시간: {elapsed:.1f}s ===")

    # 19. 로그 파일 정리
    try:
        logger.cleanup_old_logs()
    except Exception as e:
        print(f"[오류] 로그 정리 실패: {e}")

if __name__ == "__main__":
    main()
