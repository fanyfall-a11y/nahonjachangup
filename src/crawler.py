import requests
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
import config

def _normalize_program(raw: dict, source: str) -> dict:
    """
    원본 데이터를 표준 스키마로 변환하는 내부 함수
    """
    # 날짜 문자열 파싱 시도 (예: "2023.01.01 ~ 2023.12.31")
    period = raw.get("period", "")
    start_date = ""
    end_date = ""
    
    if period:
        # '~' 또는 '-'를 기준으로 날짜 분리 시도
        date_parts = re.split(r'~|-', period)
        if len(date_parts) >= 2:
            start_date = date_parts[0].strip()
            end_date = date_parts[1].strip()
        else:
            start_date = period.strip()

    standard = {
        "id": raw.get("id", ""),
        "title": raw.get("title", ""),
        "agency": raw.get("agency", ""),
        "field": raw.get("field", ""),
        "start_date": start_date,
        "end_date": end_date,
        "status": raw.get("status", ""),
        "detail_url": raw.get("detail_url", ""),
        "source": source,
        "collected_at": datetime.now().isoformat()
    }
    return standard

def crawl_bizinfo_list() -> list[dict]:
    """
    bizinfo.go.kr 사업 공고 목록을 크롤링하는 함수
    """
    url = "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do"
    headers = {
        "User-Agent": "GovSupportBot/1.0"
    }
    results = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8' # 또는 'euc-kr' 필요시 확인 (보통 UTF-8)

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.select_one("table.bbs_list_table")
        
        if not table:
            return results

        rows = table.select("tbody tr")
        for row in rows:
            try:
                # 사업명 추출
                subject_tag = row.select_one("td.subject a")
                title = subject_tag.get_text(strip=True) if subject_tag else ""
                detail_url = subject_tag.get('href', '') if subject_tag else ""
                
                # 링크가 상대 경로인 경우 절대 경로로 변환
                if detail_url and not detail_url.startswith('http'):
                    if detail_url.startswith('/'):
                        detail_url = f"https://www.bizinfo.go.kr{detail_url}"
                    else:
                        # JavaScript 함수 등이 포함된 경우 처리 불가하므로 빈 문자열 유지
                        detail_url = ""

                # 기관명 추출 (td:nth-of-type(2))
                cols = row.select("td")
                agency = ""
                if len(cols) > 1:
                    agency = cols[1].get_text(strip=True)

                # 기간 추출 (td:nth-of-type(3))
                period = ""
                if len(cols) > 2:
                    period = cols[2].get_text(strip=True)

                raw_data = {
                    "title": title,
                    "agency": agency,
                    "period": period,
                    "detail_url": detail_url
                }

                results.append(_normalize_program(raw_data, "bizinfo_crawl"))

            except Exception as e:
                # 개별 행 파싱 오류 시 무시하고 다음 행으로 진행
                continue

        time.sleep(config.REQUEST_DELAY)

    except Exception as e:
        # 전체 요청 파싱 오류 시 빈 리스트 반환
        return []

    return results

def crawl_kstartup_list() -> list[dict]:
    """
    k-startup.go.kr 진행 중인 사업 목록을 크롤링하는 함수
    """
    url = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
    headers = {
        "User-Agent": "GovSupportBot/1.0"
    }
    results = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')
        list_container = soup.select_one("ul.list-type02")
        
        if not list_container:
            return results

        items = list_container.select("li")
        for item in items:
            try:
                # 사업명 추출
                title_tag = item.select_one(".tit")
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                # 상세 링크 추출 (보통 .tit 안에 a 태그 존재)
                detail_url = ""
                if title_tag:
                    link_tag = title_tag.find("a")
                    if link_tag and link_tag.has_attr('href'):
                        href = link_tag['href']
                        if href.startswith('/'):
                            detail_url = f"https://www.k-startup.go.kr{href}"
                        elif href.startswith('http'):
                            detail_url = href
                        else:
                            detail_url = ""

                # 기관명 추출
                agency_tag = item.select_one(".name")
                agency = agency_tag.get_text(strip=True) if agency_tag else ""

                # 기간 추출
                period_tag = item.select_one(".date")
                period = period_tag.get_text(strip=True) if period_tag else ""

                raw_data = {
                    "title": title,
                    "agency": agency,
                    "period": period,
                    "detail_url": detail_url
                }

                results.append(_normalize_program(raw_data, "kstartup_crawl"))

            except Exception as e:
                # 개별 항목 파싱 오류 시 무시하고 다음 항목으로 진행
                continue

        time.sleep(config.REQUEST_DELAY)

    except Exception as e:
        # 전체 요청 파싱 오류 시 빈 리스트 반환
        return []

    return results

def crawl_all_fallback() -> list[dict]:
    """
    폴백 모드가 활성화된 경우 모든 크롤러를 실행하고 결과를 합산하여 반환
    """
    if not config.CRAWL_FALLBACK:
        return []

    bizinfo_list = crawl_bizinfo_list()
    kstartup_list = crawl_kstartup_list()

    return bizinfo_list + kstartup_list
