from flask import Flask, send_file
from PIL import Image, ImageDraw
import datetime
import io

app = Flask(__name__)

def calculate_result_by_hashing(seed):
    hash_val = int(seed) * 16777619
    hash_val = (hash_val ^ (hash_val >> 13)) * 131
    hash_val = (hash_val ^ (hash_val >> 15))
    hex_str = hex(hash_val).upper()
    last_char = hex_str[-1]
    try:
        last_digit = int(last_char, 16)
    except:
        last_digit = 0
    return "ODD" if last_digit % 2 != 0 else "EVEN" # 한글 깨짐 방지를 위해 영어 사용

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_result(path):
    try:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        kst_timestamp_ms = int(now.timestamp() * 1000)
        cycle_duration_ms = 4 * 60 * 1000
        current_seed = kst_timestamp_ms // cycle_duration_ms
        result = calculate_result_by_hashing(current_seed)
        
        # 이미지 생성 (배경 어둡게 해서 고급스럽게)
        img = Image.new('RGB', (400, 250), color='#2C3E50')
        d = ImageDraw.Draw(img)
        
        # 결과에 따른 배경색 설정
        res_bg = "#E74C3C" if result == "ODD" else "#3498DB" # 빨강 / 파랑
        
        # 중앙 박스 그리기 (글자 대신 박스로 강조)
        d.rectangle([100, 70, 300, 150], fill=res_bg, outline="white", width=3)
        
        # 텍스트들
        d.text((110, 30), "YGOSU 4MIN REALTIME", fill="#ECF0F1")
        d.text((175, 100), result, fill="white") # 결과값 (ODD/EVEN)
        
        # 타이머 및 하단 정보
        remaining = 240 - (int(now.timestamp()) % 240)
        timer_str = f"NEXT: {remaining // 60:02d}:{remaining % 60:02d}"
        d.text((160, 170), timer_str, fill="#F1C40F")
        d.text((120, 210), f"UPDATE: {now.strftime('%H:%M:%S')}", fill="#BDC3C7")

        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return str(e), 500
