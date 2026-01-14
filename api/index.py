from flask import Flask, send_file
from PIL import Image, ImageDraw
import datetime
import io

app = Flask(__name__)

def calculate_result(seed):
    # game.html 해싱 로직
    hash_val = int(seed) * 16777619
    hash_val = (hash_val ^ (hash_val >> 13)) * 131
    hash_val = (hash_val ^ (hash_val >> 15))
    last_char = hex(hash_val)[-1]
    try:
        digit = int(last_char, 16)
    except:
        digit = 0
    return "ODD" if digit % 2 != 0 else "EVEN"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    try:
        # 1. 시간 및 결과 계산
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        seed = int(now.timestamp()) // 240
        result = calculate_result(seed)
        
        # 2. 이미지 그리기
        img = Image.new('RGB', (400, 250), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 테두리 및 디자인
        res_color = "#E74C3C" if result == "ODD" else "#337AB7"
        d.rectangle([10, 10, 390, 240], outline="#4A90E2", width=5)
        d.rectangle([130, 70, 270, 140], fill=res_color)
        
        # 텍스트 배치
        d.text((100, 30), "YGOSU 4MIN REALTIME", fill="#333333")
        d.text((175, 95), result, fill="white")
        
        rem = 240 - (int(now.timestamp()) % 240)
        d.text((160, 160), f"NEXT: {rem // 60:02d}:{rem % 60:02d}", fill="#4A90E2")
        d.text((125, 200), f"REFRESH: {now.strftime('%H:%M:%S')}", fill="#999999")

        # 3. 이미지 전송 (가장 안전한 방식)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return str(e), 500
