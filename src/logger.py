import logging
import os
from datetime import datetime, timedelta
import config

def get_logger(name) -> logging.Logger:
    """
    로거를 생성하고 설정합니다.
    logs/YYYY-MM-DD.log 파일과 콘솔에 동시에 출력합니다.
    """
    try:
        # 로그 디렉토리가 없으면 생성
        if not os.path.exists(config.LOG_DIR):
            os.makedirs(config.LOG_DIR)

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO) # 필요시 DEBUG 등으로 변경

        # 핸들러가 이미 추가되어 있지 않은 경우에만 추가 (중복 방지)
        if not logger.handlers:
            # 로그 포맷 설정
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

            # 파일 핸들러 설정 (날짜별 파일)
            log_filename = f"{datetime.now().strftime('%Y-%m-%d')}.log"
            file_path = os.path.join(config.LOG_DIR, log_filename)
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)

            # 콘솔 핸들러 설정
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            # 로거에 핸들러 추가
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger
    except Exception as e:
        # 로거 설정 실패 시 기본 로거 반환 및 에러 출력
        print(f"로거 설정 중 오류 발생: {e}")
        return logging.getLogger(name)

def log_run_start() -> None:
    """루트 로거로 수집 시작 로그를 기록합니다."""
    try:
        logger = logging.getLogger()
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"=== 수집 시작 ({now_str}) ===")
    except Exception as e:
        print(f"시작 로그 기록 중 오류 발생: {e}")

def log_run_result(total_raw, total_filtered, urgent, saved_path) -> None:
    """루트 로거로 수집 결과 요약을 기록합니다."""
    try:
        logger = logging.getLogger()
        logger.info("=== 수집 결과 요약 ===")
        logger.info(f"총 원본: {total_raw}, 필터링된 수: {total_filtered}, 긴급 건수: {urgent}")
        logger.info(f"저장 경로: {saved_path}")
    except Exception as e:
        print(f"결과 로그 기록 중 오류 발생: {e}")

def cleanup_old_logs() -> None:
    """
    설정된 보관 기일(LOG_RETENTION_DAYS)이 지난 .log 파일을 삭제합니다.
    """
    try:
        if not os.path.exists(config.LOG_DIR):
            return

        # 삭제 기준 날짜 계산
        cutoff_date = datetime.now() - timedelta(days=config.LOG_RETENTION_DAYS)

        for filename in os.listdir(config.LOG_DIR):
            if filename.endswith(".log"):
                file_path = os.path.join(config.LOG_DIR, filename)
                try:
                    # 파일 수정 시간 확인
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # 기준 날짜보다 오래된 파일 삭제
                    if file_mtime < cutoff_date:
                        os.remove(file_path)
                        print(f"오래된 로그 삭제 완료: {filename}")
                except Exception as e:
                    print(f"파일 삭제 중 오류 발생 ({filename}): {e}")

    except Exception as e:
        print(f"로그 정리 중 오류 발생: {e}")
