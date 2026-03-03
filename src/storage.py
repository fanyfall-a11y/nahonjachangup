import json
import os
from datetime import datetime
import config


def ensure_output_dir(dirpath: str) -> None:
    """
    디렉토리가 존재하지 않으면 생성하는 함수
    """
    try:
        os.makedirs(dirpath, exist_ok=True)
    except Exception as e:
        print(f"[오류] 디렉토리 생성 실패: {e}")


def save_as_json(programs: list[dict], filepath: str) -> str:
    """
    프로그램 리스트를 JSON 형식으로 저장하는 함수
    """
    try:
        data = {
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "total_count": len(programs),
            "programs": programs
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return filepath
    except Exception as e:
        print(f"[오류] JSON 저장 실패: {e}")
        return ""


def save_as_markdown(programs: list[dict], filepath: str) -> str:
    """
    프로그램 리스트를 Markdown 형식으로 저장하는 함수
    """
    try:
        lines = []
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 헤더 작성
        lines.append(f"# 정부지원사업 안내 ({today_str})")
        lines.append("")
        
        for idx, prog in enumerate(programs, 1):
            # 딕셔너리 키 추출
            title = prog.get('title', '제목 없음')
            agency = prog.get('agency', '-')
            field = prog.get('field', '-')
            end_date = prog.get('end_date', '-')
            status = prog.get('status', '-')
            url = prog.get('detail_url', '-')
            
            # 긴급 표시 확인
            prefix = "[긴급] " if status == "마감임박" else ""
            
            # 사업명 헤더 작성
            lines.append(f"## [{idx}] {prefix}{title}")
            lines.append("")
            
            # 상세 내용 리스트 작성
            lines.append(f"- 기관: {agency}")
            lines.append(f"- 분야: {field}")
            lines.append(f"- 마감일: {end_date}")
            lines.append(f"- 상태: {status}")
            lines.append(f"- URL: {url}")
            lines.append("")  # 항목 간 구분
        
        content = "\n".join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return filepath
    except Exception as e:
        print(f"[오류] Markdown 저장 실패: {e}")
        return ""


def save_content_files(programs: list[dict], content: dict, date_str: str) -> list[str]:
    """
    Gemini 생성 콘텐츠를 프로그램별 텍스트 파일로 저장하는 함수.
    멘트요약 / 네이버블로그 / 티스토리 / 블로그스팟 파일을 생성한다.
    """
    saved = []
    ensure_output_dir(config.OUTPUT_DIR)

    insta_list = content.get("instagram", [])
    naver_list = content.get("naver", [])
    tistory_list = content.get("tistory", [])
    blogspot_list = content.get("blogspot", [])

    for i, prog in enumerate(programs):
        title = prog.get("title", "")
        period = prog.get("period", "") or f"{prog.get('start_date','')} ~ {prog.get('end_date','')}"
        contact = prog.get("contact", "")
        url = prog.get("detail_url", "")
        target = prog.get("target", "")
        field = prog.get("field", "")
        idx = i + 1

        # 00_멘트_요약.txt
        try:
            ment = insta_list[i] if i < len(insta_list) else ""
            lines = [
                f"[{title}]",
                "",
                "📌 핵심 멘트 (카드뉴스용):",
                ment,
                "",
                "👥 신청자격:",
                target,
                "",
                "💰 지원분야:",
                field,
                "",
                "📅 신청기간:",
                period,
            ]
            if contact:
                lines += ["", "📞 문의:", contact]
            if url:
                lines += ["", "🔗 링크:", url]

            path = os.path.join(config.OUTPUT_DIR, f"{date_str}_{idx:02d}_멘트요약.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            saved.append(path)
        except Exception as e:
            print(f"[오류] 멘트요약 저장 실패 ({idx}): {e}")

        # 플랫폼별 블로그 글 저장
        platform_map = [
            ("네이버블로그", naver_list),
            ("티스토리", tistory_list),
            ("블로그스팟", blogspot_list),
        ]
        for platform_name, plist in platform_map:
            if i < len(plist):
                try:
                    path = os.path.join(config.OUTPUT_DIR, f"{date_str}_{idx:02d}_{platform_name}.txt")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(plist[i])
                    saved.append(path)
                except Exception as e:
                    print(f"[오류] {platform_name} 저장 실패 ({idx}): {e}")

    return saved


def save(programs: list[dict]) -> str:
    """
    설정에 따라 적절한 형식으로 파일을 저장하는 메인 함수
    """
    try:
        # 출력 디렉토리 확인 및 생성
        ensure_output_dir(config.OUTPUT_DIR)
        
        # 파일명 생성 (날짜 포함)
        today_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today_str}_programs"
        
        saved_path = ""
        
        if config.OUTPUT_FORMAT == "json":
            full_path = os.path.join(config.OUTPUT_DIR, f"{filename}.json")
            saved_path = save_as_json(programs, full_path)
        else:
            full_path = os.path.join(config.OUTPUT_DIR, f"{filename}.md")
            saved_path = save_as_markdown(programs, full_path)
            
        return saved_path
    except Exception as e:
        print(f"[오류] 저장 처리 중 실패: {e}")
        return ""
