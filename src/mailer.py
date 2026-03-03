import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import config


def send_daily_report(programs: list[dict], content: dict, image_paths: list[str]) -> bool:
    """
    정부지원사업 일일 리포트를 Gmail SMTP를 통해 발송하는 함수입니다.
    """

    # config.EMAIL_FROM 또는 config.EMAIL_PASSWORD가 비어있으면 False 반환 + 경고 출력
    if not config.EMAIL_FROM or not config.EMAIL_PASSWORD:
        print("경고: 이메일 발신자 주소 또는 비밀번호가 설정되지 않았습니다.")
        return False

    # config.EMAIL_TO가 비어있으면 False 반환
    if not config.EMAIL_TO:
        print("경고: 이메일 수신자 주소가 설정되지 않았습니다.")
        return False

    # 오늘 날짜 포맷팅
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    today_display = f"{now.year}. {now.month}. {now.day}."

    # 이메일 제목 설정
    subject = f"[나혼자창업] {today} 신규 지원사업 {len(programs)}건 안내"

    # 인스타그램 멘트 리스트 (프로그램별 💬 멘트용)
    insta_list = content.get("instagram", [])

    # 이메일 본문 구성 (텍스트 형식)
    lines = []
    lines.append(f"📬 나혼자창업 신규 지원사업 알림")
    lines.append(f"📅 {today_display} 기준 {len(programs)}건")
    lines.append("=" * 50)
    lines.append("")

    for i, prog in enumerate(programs):
        title = prog.get('title', '')
        period = prog.get('period', '') or f"{prog.get('start_date','')} ~ {prog.get('end_date','')}"
        url = prog.get('detail_url', '')
        target = prog.get('target', '')
        status = prog.get('status', '')

        # 💬 멘트: Gemini 인스타 캡션 우선, 없으면 기본 텍스트
        ment = insta_list[i] if i < len(insta_list) else f"{title} 공고가 등록되었습니다."
        # 첫 줄만 사용 (너무 길면 잘라냄)
        ment_short = ment.split('\n')[0][:120]

        lines.append(f"【{i+1}】 {title}")
        lines.append(f"💬 {ment_short}")
        if target:
            lines.append(f"👥 {target}")
        if period.strip():
            lines.append(f"📅 {period}")
        if url:
            lines.append(f"🔗 {url}")
        if status == "마감임박":
            lines.append("⚠️ 마감임박!")
        lines.append("-" * 50)
        lines.append("")

    body = "\n".join(lines)

    # 메시지 객체 생성
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = config.EMAIL_FROM

    # 카드뉴스 이미지 전체 첨부
    for img_path in image_paths:
        try:
            with open(img_path, 'rb') as f:
                img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(img_path))
            msg.attach(image)
        except Exception as e:
            print(f"이미지 첨부 중 오류 발생 ({img_path}): {e}")

    # 텍스트 본문 첨부
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # SMTP 발송 처리
    try:
        # SMTP 서버 연결 및 로그인
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(config.EMAIL_FROM, config.EMAIL_PASSWORD)

            # 수신자 리스트 처리 (문자열 또는 리스트 모두 지원)
            recipients = config.EMAIL_TO if isinstance(config.EMAIL_TO, list) else [config.EMAIL_TO]

            # 각 수신자에게 발송
            for recipient in recipients:
                msg['To'] = recipient
                server.sendmail(config.EMAIL_FROM, recipient, msg.as_string())

        return True

    except Exception as e:
        print(f"이메일 발송 실패: {e}")
        return False
