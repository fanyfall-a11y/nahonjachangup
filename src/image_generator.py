from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
from datetime import datetime
import config

def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """
    시스템 환경에 맞는 한국어 폰트를 로드하여 반환합니다.
    지정된 경로의 폰트를 순차적으로 시도하며, 모두 실패하면 기본 폰트를 반환합니다.
    """
    font_paths = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]
    
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
            
    try:
        return ImageFont.load_default()
    except Exception:
        # 최악의 경우 None 반환 (호출 측에서 처리 필요할 수 있음)
        return None

def _wrap_text(text: str, width: int) -> str:
    """
    주어진 텍스트를 지정된 너비에 맞춰 줄바꿈 처리합니다.
    """
    try:
        return textwrap.fill(text, width=width)
    except Exception:
        return text

def create_card(program: dict, card_index: int, date_str: str) -> str:
    """
    인스타그램 카드뉴스 이미지 1장을 생성하고 저장합니다.
    """
    # 이미지 크기 설정
    img_width = config.IMAGE_WIDTH
    img_height = config.IMAGE_HEIGHT
    
    # 이미지 객체 생성 (배경색: 브랜드 프라이머리 컬러)
    try:
        image = Image.new('RGB', (img_width, img_height), config.BRAND_COLOR_PRIMARY)
        draw = ImageDraw.Draw(image)
    except Exception as e:
        print(f"이미지 초기화 실패: {e}")
        return ""

    # 영역 높이 계산
    top_h = int(img_height * 0.2)      # 상단 20%
    bottom_h = int(img_height * 0.1)   # 하단 10%
    middle_h = img_height - top_h - bottom_h # 중앙 70%

    # 폰트 로드
    try:
        brand_font = _get_font(80)
        index_font = _get_font(50)
        header_font = _get_font(60)
        body_font = _get_font(50)
    except Exception as e:
        print(f"폰트 로딩 실패: {e}")
        return ""

    # 1. 상단 영역: 브랜드명 ("나혼자창업")
    try:
        # 텍스트 가로길이 계산 (중앙 정렬용)
        bbox = draw.textbbox((0, 0), "나혼자창업", font=brand_font)
        text_w = bbox[2] - bbox[0]
        draw.text(((img_width - text_w) / 2, (top_h - 80) / 2), "나혼자창업", font=brand_font, fill="white")
    except Exception:
        pass

    # 2. 하단 영역: 카드 인덱스 ("{card_index}/5")
    try:
        index_text = f"{card_index}/5"
        bbox = draw.textbbox((0, 0), index_text, font=index_font)
        text_w = bbox[2] - bbox[0]
        draw.text(((img_width - text_w) / 2, top_h + middle_h + (bottom_h - 50) / 2), index_text, font=index_font, fill="white")
    except Exception:
        pass

    # 3. 중앙 영역: 흰색 사각형 배경
    box_margin = 40
    draw.rectangle(
        [box_margin, top_h + box_margin, img_width - box_margin, top_h + middle_h - box_margin], 
        fill="white"
    )

    # 카드 내용 데이터 설정
    content = ""
    header = ""
    
    try:
        if card_index == 1:
            content = program.get('title', '제목 정보 없음')
        elif card_index == 2:
            header = "신청자격"
            content = program.get('agency', '기관 정보 없음')
        elif card_index == 3:
            header = "지원내용"
            content = program.get('field', '분야 정보 없음')
        elif card_index == 4:
            header = "신청기간"
            content = f"{program.get('start_date', '')} ~ {program.get('end_date', '')}"
        elif card_index == 5:
            # CTA 메시지 (헤더 없음)
            content = "구독과 좋아요는 큰 힘이 됩니다\n나혼자창업"
    except Exception:
        content = "정보를 불러올 수 없습니다."

    # 4. 중앙 텍스트 그리기
    box_inner_width = img_width - (box_margin * 2)
    current_y = top_h + box_margin + 60 # 시작 위치 여백

    # 헤더 그리기 (카드 1, 5 제외)
    if header:
        try:
            bbox = draw.textbbox((0, 0), header, font=header_font)
            text_w = bbox[2] - bbox[0]
            draw.text(((img_width - text_w) / 2, current_y), header, font=header_font, fill="black")
            current_y += 100 # 헤더와 본문 간격
        except Exception:
            pass

    # 본문 그리기
    try:
        # 줄바꿈 처리 (대략 25자 기준)
        wrapped_content = _wrap_text(content, width=25)
        lines = wrapped_content.split('\n')
        
        # CTA(카드5)인 경우 중앙 정렬을 위해 전체 높이 계산
        if card_index == 5:
            lines = content.split('\n') # CTA는 개행문자 기준 유지
            total_text_height = len(lines) * 60
            current_y = top_h + (middle_h - total_text_height) / 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=body_font)
            text_w = bbox[2] - bbox[0]
            draw.text(((img_width - text_w) / 2, current_y), line, font=body_font, fill="black")
            current_y += 60 # 줄 간격
    except Exception:
        pass

    # 파일 저장
    filename = f"{date_str}_card_{card_index}.png"
    save_path = config.IMAGE_DIR + filename
    
    try:
        image.save(save_path)
    except Exception as e:
        print(f"이미지 저장 실패 ({save_path}): {e}")
        return ""

    return save_path

def create_card_set(program: dict, date_str: str) -> list[str]:
    """
    5장의 카드뉴스 세트를 생성합니다.
    저장 디렉토리가 없으면 생성합니다.
    """
    saved_paths = []

    try:
        # 디렉토리 확인 및 생성
        if not os.path.exists(config.IMAGE_DIR):
            os.makedirs(config.IMAGE_DIR)
    except Exception as e:
        print(f"디렉토리 생성 실패: {e}")
        return []

    # 1~5장 생성 루프
    try:
        for i in range(1, config.IMAGE_CARDS_COUNT + 1):
            path = create_card(program, i, date_str)
            if path:
                saved_paths.append(path)
    except Exception as e:
        print(f"카드 생성 중 오류 발생: {e}")

    return saved_paths
