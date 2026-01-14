from flask import Flask, send_file
from PIL import Image, ImageDraw
import datetime
import io

app = Flask(__name__)

def calculate_result(seed):
    # 사용자님의 자바스크립트 해싱 로직을 파이썬으로 동일하게 구현
    hash_val = seed * 16777619
    hash_val = (hash_val ^ (hash_val >> 13)) * 131
    hash_val = (hash_val ^ (hash_val >> 15))
    
    # 16진수 마지막 자리 숫자로 홀짝 결정
    last_digit = int(hex(hash_val)[-1], 16)
    return "홀" if last_digit % 2 != 0 else "짝"

@app.route('/api/index')
def get_result():
    # 1. 한국 시간 가져오기
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    
    # 2. 4분 주기(240초) 시드 계산
    timestamp = int(now.timestamp())
    current_seed = timestamp // 240
    
    # 3. 결과 계산
    result_text = calculate_result(current_seed)
    
    # 4. 다음 변경까지 남은 시간 계산
    remaining_sec = 240 - (timestamp % 240)
    minutes = remaining_sec // 60
    seconds = remaining_sec % 60
    timer_str = f"{minutes:02d}:{seconds:02d}"

    # 5. 이미지 생성 (디자인 적용)
    img = Image.new('RGB', (400, 250), color='#FFFFFF')
    d = ImageDraw.Draw(img)
    
    # 테두리
    d.rectangle([5, 5, 395, 245], outline="#4A90E2", width=5)
    
    # 텍스트 그리기
    color = "#e74c3c" if result_text == "홀" else "#337ab7"
    d.text((100, 30), "🎲 와이고수 4분주기 결과", fill="#333333")
    d.text((150, 70), result_text, fill=color) # 결과값
    d.text((160, 150), timer_str, fill="#4A90E2") # 남은 시간
    d.text((90, 200), f"갱신: {now.strftime('%y.%m.%d %H:%M')}", fill="#999999")

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')
