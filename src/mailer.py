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
    today = datetime.now().strftime("%Y-%m-%d")

    # 이메일 제목 설정
    subject = f"[나혼자창업] {today} 정부지원사업 {len(programs)}건 안내"

    # HTML 본문 구성 시작
    html = f"""
    <html>
    <body>
        <h2>오늘의 정부지원사업 안내</h2>
        <p>수집일: {today}</p>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <thead>
                <tr style="background-color: #f2f2f2; text-align: left;">
                    <th style="padding: 8px;">제목</th>
                    <th style="padding: 8px;">기관</th>
                    <th style="padding: 8px;">마감일</th>
                    <th style="padding: 8px;">상태</th>
                </tr>
            </thead>
            <tbody>
    """

    # 프로그램 목록 테이블 생성
    for prog in programs:
        title = prog.get('title', '')
        agency = prog.get('agency', '')
        end_date = prog.get('end_date', '')
        status = prog.get('status', '')

        # 마감임박 공고(status=="마감임박")인 경우 빨간 텍스트 강조
        style_attr = "color: red; font-weight: bold;" if status == "마감임박" else ""

        html += f"""
                <tr>
                    <td style="padding: 8px;">{title}</td>
                    <td style="padding: 8px;">{agency}</td>
                    <td style="padding: 8px;">{end_date}</td>
                    <td style="padding: 8px; {style_attr}">{status}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>
        <br/>
    """

    # 블로그 콘텐츠 섹션 (content.get("naver", []) 첫 번째 항목)
    naver_list = content.get("naver", [])
    if naver_list:
        html += f"""
        <h3>블로그 콘텐츠</h3>
        <p>{naver_list[0]}</p>
        <br/>
        """

    # 인스타그램 멘트 (content.get("instagram", []) 첫 번째 항목)
    insta_list = content.get("instagram", [])
    if insta_list:
        html += f"""
        <h3>인스타그램 멘트</h3>
        <p>{insta_list[0]}</p>
        """

    html += """
    </body>
    </html>
    """

    # 메시지 객체 생성
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = config.EMAIL_FROM

    # image_paths 첫 번째 이미지 첨부 (MIMEImage, 없으면 건너뜀)
    if image_paths:
        try:
            with open(image_paths[0], 'rb') as f:
                img_data = f.read()
            image = MIMEImage(img_data, name=os.path.basename(image_paths[0]))
            msg.attach(image)
        except Exception as e:
            print(f"이미지 첨부 중 오류 발생: {e}")
            # 이미지 첨부 실패 시 이메일 발송은 계속 진행

    # HTML 본문 첨부
    msg.attach(MIMEText(html, 'html'))

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
