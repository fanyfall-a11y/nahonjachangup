import requests
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import config


def _normalize_date(date_str: str) -> str:
    """
    날짜 문자열을 YYYY-MM-DD 형식으로 통일
    지원 형식: YYYYMMDD, YYYY-MM-DD, YYYY.MM.DD
    """
    if not date_str:
        return ""
    
    try:
        # 구분자 제거
        clean_str = date_str.replace(".", "").replace("-", "").replace("/", "")
        
        # 8자리(YYYYMMDD)인 경우 파싱
        if len(clean_str) == 8:
            year = clean_str[:4]
            month = clean_str[4:6]
            day = clean_str[6:8]
            return f"{year}-{month}-{day}"
        
        # 그 외의 경우 datetime으로 파싱 시도
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""


def fetch_bizinfo_programs(page: int) -> list[dict]:
    """
    기업마당 API 호출 및 데이터 파싱
    """
    if not config.BIZINFO_API_KEY:
        return []

    try:
        url = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
        params = {
            "crtfcKey": config.BIZINFO_API_KEY,
            "pageUnit": config.ROWS_PER_PAGE,
            "pageIndex": page,
            "bsnsSe": "ALL"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # XML 파싱
        root = ET.fromstring(response.content)
        results = []
        
        # item 태그 찾기
        for item in root.findall('.//item'):
            try:
                program = {
                    "id": item.findtext('pblancId', ''),
                    "title": item.findtext('pblancNm', ''),
                    "agency": item.findtext('insttNm', ''),
                    "field": item.findtext('pldirSportRealmLclasCode', ''),
                    "start_date": _normalize_date(item.findtext('reqstBgngDt', '')),
                    "end_date": _normalize_date(item.findtext('reqstEndDt', '')),
                    "detail_url": item.findtext('detailUrl', ''),
                    "source": "bizinfo_api",
                    "status": "",
                    "collected_at": datetime.now().isoformat()
                }
                results.append(program)
            except Exception as parse_err:
                print(f"XML item parsing error: {parse_err}")
                continue

        return results

    except Exception as e:
        print(f"기업마당 API 호출 오류: {e}")
        return []
    finally:
        time.sleep(config.REQUEST_DELAY)


def fetch_kstartup_programs(page: int) -> list[dict]:
    """
    K-Startup API 호출 및 데이터 파싱
    """
    if not config.KSTARTUP_API_KEY:
        return []

    try:
        url = "https://api.odcloud.kr/api/15125364/v1/uddi:2c5e4c84-4b9b-4c87-8b1e-5b8e1e5b8e1e"
        params = {
            "serviceKey": config.KSTARTUP_API_KEY,
            "page": page,
            "perPage": config.ROWS_PER_PAGE,
            "returnType": "json"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        data_list = json_data.get('data', [])
        
        results = []
        for item in data_list:
            try:
                # ID 필드가 명시되어 있지 않으나 공통 스키마 유지를 위해 시도
                p_id = item.get('id') or item.get('pblancId') or item.get('sn') or ""
                
                program = {
                    "id": p_id,
                    "title": item.get('사업명', ''),
                    "agency": item.get('공고기관', ''),
                    "field": item.get('분야', ''),
                    "start_date": _normalize_date(item.get('접수시작일', '')),
                    "end_date": _normalize_date(item.get('접수종료일', '')),
                    "detail_url": item.get('공고URL', ''),
                    "source": "kstartup_api",
                    "status": "",
                    "collected_at": datetime.now().isoformat()
                }
                results.append(program)
            except Exception as parse_err:
                print(f"JSON item parsing error: {parse_err}")
                continue

        return results

    except Exception as e:
        print(f"K-Startup API 호출 오류: {e}")
        return []


def fetch_all_api_programs() -> list[dict]:
    """
    설정된 최대 페이지 수만큼 모든 API 호출 및 중복 제거 수행
    """
    all_programs = []
    seen_ids = set()

    try:
        for page in range(1, config.MAX_PAGES + 1):
            # 기업마당 데이터 수집
            biz_list = fetch_bizinfo_programs(page)
            for item in biz_list:
                if item['id'] not in seen_ids:
                    seen_ids.add(item['id'])
                    all_programs.append(item)
            
            # K-Startup 데이터 수집
            k_start_list = fetch_kstartup_programs(page)
            for item in k_start_list:
                # ID가 없는 경우 중복 제거가 어려우므로 title을 키로 사용하거나 그냥 추가
                # 여기서는 id가 없는 경우도 포함하여 처리
                unique_key = item['id'] if item['id'] else item['title']
                if unique_key not in seen_ids:
                    seen_ids.add(unique_key)
                    all_programs.append(item)

    except Exception as e:
        print(f"전체 데이터 수집 중 오류 발생: {e}")

    return all_programs
