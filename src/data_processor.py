from datetime import datetime, timedelta
import config


def deduplicate(programs: list[dict]) -> list[dict]:
    """
    title과 agency 조합을 키로 사용하여 중복된 항목을 제거합니다.
    """
    try:
        unique_programs = []
        seen_keys = set()
        
        for program in programs:
            # 데이터 안전성 확보를 위해 get 메서드 사용
            key = (program.get('title', ''), program.get('agency', ''))
            
            if key not in seen_keys:
                seen_keys.add(key)
                unique_programs.append(program)
                
        return unique_programs
    except Exception as e:
        print(f"[오류] 중복 제거 실패: {e}")
        return []


def filter_by_keywords(programs: list[dict]) -> list[dict]:
    """
    설정된 키워드(config.FILTER_KEYWORDS)가 title 또는 agency에 포함된 항목만 반환합니다.
    대소문자는 무시합니다.
    """
    try:
        # 키워드가 없으면 전체 반환
        if not config.FILTER_KEYWORDS:
            return programs
        
        # 대소문자 무시 검색을 위해 키워드 소문자 변환
        keywords_lower = [k.lower() for k in config.FILTER_KEYWORDS]
        filtered_programs = []
        
        for program in programs:
            title = program.get('title', '').lower()
            agency = program.get('agency', '').lower()
            
            # 키워드 중 하나라도 포함되면 통과
            if any(keyword in title or keyword in agency for keyword in keywords_lower):
                filtered_programs.append(program)
                
        return filtered_programs
    except Exception as e:
        print(f"[오류] 키워드 필터링 실패: {e}")
        return []


def filter_by_deadline(programs: list[dict]) -> list[dict]:
    """
    오늘 날짜 기준으로 config.DEADLINE_DAYS_AHEAD일 이내에 마감되는 항목만 반환합니다.
    이미 마감된 항목은 제외하며, 날짜가 없는 항목은 포함합니다.
    """
    try:
        today = datetime.now()
        deadline_limit = today + timedelta(days=config.DEADLINE_DAYS_AHEAD)
        
        filtered_programs = []
        
        for program in programs:
            end_date_str = program.get('end_date', '')
            
            # 마감일이 비어있으면 날짜 미상으로 간주하여 포함
            if not end_date_str:
                filtered_programs.append(program)
                continue
            
            try:
                # 날짜 포맷 변환 (YYYY-MM-DD 가정)
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                
                # 오늘 이후이며 설정된 기간 이내인 항목만 통과
                if today <= end_date <= deadline_limit:
                    filtered_programs.append(program)
            except ValueError:
                # 날짜 포맷이 잘못된 경우 건너뜀
                continue
                
        return filtered_programs
    except Exception as e:
        print(f"[오류] 마감일 필터링 실패: {e}")
        return []


def assign_status(programs: list[dict]) -> list[dict]:
    """
    각 사업의 날짜 정보를 바탕으로 status 필드를 부여합니다.
    """
    try:
        today = datetime.now()
        urgent_limit = today + timedelta(days=config.URGENT_DAYS)
        
        processed_programs = []
        
        for program in programs:
            # 원본 데이터 변경 방지를 위해 복사 (선택사항이나 권장됨)
            new_program = program.copy()
            end_date_str = new_program.get('end_date', '')
            start_date_str = new_program.get('start_date', '')
            
            status = "모집중" # 기본값
            
            # 시작일이 미래인 경우 '예정'
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    if start_date > today:
                        status = "예정"
                except ValueError:
                    pass
            
            # '예정' 상태가 아니며 마감일이 있는 경우 마감 상태 판별
            if status != "예정":
                if not end_date_str:
                    status = "모집중"
                else:
                    try:
                        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                        
                        if end_date < today:
                            status = "마감"
                        elif end_date <= urgent_limit:
                            status = "마감임박"
                        else:
                            status = "모집중"
                    except ValueError:
                        status = "모집중" # 파싱 실패 시 기본값
            
            new_program['status'] = status
            processed_programs.append(new_program)
            
        return processed_programs
    except Exception as e:
        print(f"[오류] 상태 부여 실패: {e}")
        return []


def sort_by_deadline(programs: list[dict]) -> list[dict]:
    """
    마감일(end_date)을 기준으로 오름차순 정렬합니다.
    마감일이 없는 항목은 리스트의 맨 뒤로 배치됩니다.
    """
    try:
        def get_sort_key(item):
            end_date_str = item.get('end_date', '')
            if not end_date_str:
                return datetime.max # 날짜가 없으면 최대값으로 처리하여 뒤로 보냄
            
            try:
                return datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                return datetime.max # 포맷 오류도 뒤로 보냄

        return sorted(programs, key=get_sort_key)
    except Exception as e:
        print(f"[오류] 정렬 실패: {e}")
        return programs


def run_pipeline(raw_programs: list[dict]) -> list[dict]:
    """
    데이터 정제 파이프라인을 순서대로 실행하고 각 단계의 건수를 출력합니다.
    순서: 중복제거 -> 키워드필터 -> 마감일필터 -> 상태부여 -> 정렬
    """
    try:
        print(">>> 데이터 파이프라인 시작")
        print(f"1. 입력 데이터 수: {len(raw_programs)}")
        
        # 1. 중복 제거
        step1 = deduplicate(raw_programs)
        print(f"2. 중복 제거 후: {len(step1)}")
        
        # 2. 키워드 필터링
        step2 = filter_by_keywords(step1)
        print(f"3. 키워드 필터링 후: {len(step2)}")
        
        # 3. 마감일 필터링
        step3 = filter_by_deadline(step2)
        print(f"4. 마감일 필터링 후: {len(step3)}")
        
        # 4. 상태 부여
        step4 = assign_status(step3)
        # 건수 변화 없음
        
        # 5. 정렬
        final_data = sort_by_deadline(step4)
        print(f"5. 최종 출력 데이터 수: {len(final_data)}")
        print(">>> 데이터 파이프라인 완료")
        
        return final_data
        
    except Exception as e:
        print(f"[오류] 파이프라인 실행 중 치명적 오류 발생: {e}")
        return []
