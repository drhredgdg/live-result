from flask import Flask, send_file
from PIL import Image, ImageDraw
import datetime
import io

app = Flask(__name__)

@app.route('/api/index')
def get_result():
    # 한국 시간 설정
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    
    # 4분 주기 홀짝 계산 로직
    # 분을 4로 나눈 몫이 홀수이면 '홀', 짝수이면 '짝'
    current_period = (now.minute // 4)
    is_odd = current_period % 2 != 0
    result_text = "홀" if is_odd else "짝"
    
    # 이미지 생성 (크기 400x250)
    img = Image.new('RGB', (400, 250), color='#ffffff')
    d = ImageDraw.Draw(img)
    
    # 디자인: 파란 테두리와 큰 글씨
    d.rectangle([5, 5, 395, 245], outline="#3a86ff", width=8)
    
    # 결과 출력 (서버 기본 폰트 사용)
    # 텍스트 위치는 대략 중앙 (x:150, y:80)
    d.text((140, 40), "[ 실시간 결과 ]", fill="#333333")
    d.text((170, 90), result_text, fill="#3a86ff") 
    d.text((90, 180), f"갱신시간: {now.strftime('%H:%M:%S')}", fill="#888888")

    # 이미지를 파일 형태로 변환하여 전송
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')
