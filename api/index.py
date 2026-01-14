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
    return "ODD" if last_digit % 2 != 0 else "EVEN"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_result(path):
    try:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        kst_ts = int(now.timestamp() * 1000)
        cycle_ms = 4 * 60 * 1000
        seed = kst_ts // cycle_ms
        result = calculate_result_by_hashing(seed)
        
        # 1. 배경 및 캔버스 (흰색 배경)
        img = Image.new('RGB', (400, 320), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 2. 메인 컨테이너 테두리 (border: 3px solid #4A90E2)
        d.rectangle([15, 15, 385, 305], outline="#4A90E2", width=4)
        
        # 3. 헤더 (🎲 와이고수 4분주기 홀짝 결과)
        d.text((85, 40), "YGOSU 4MIN ODD/EVEN", fill="#333333")
        
        # 4. 중앙 결과 표시 영역
        res_text = "ODD" if result == "ODD" else "EVEN"
        res_color = "#e74c3c" if result == "ODD" else "#337ab7"
        
        # 큰 글씨 대신 박스로 강조 (서버 폰트 한계 극복)
        d.rectangle([130, 80, 270, 150], fill=res_color)
        d.text((175, 105), res_text, fill="white")
        
        # 5. 시간 라벨 (기준 시각)
        start_ts = seed * cycle_ms
        start_dt = datetime.datetime.fromtimestamp(start_ts / 1000)
        time_label = start_dt.strftime("%y.%m.%d %H:%M")
        d.text((140, 165), time_label, fill="#666666")
        
        # 6. 타이머 (03:18) - 파란색 강조
        rem = 240 - (int(now.timestamp()) % 240)
        timer_str = f"{rem // 60:02d}:{rem % 60:02d}"
        d.text((175, 200), timer_str, fill="#4A90E2")
        
        # 7. 다음 결과 변경 시각
        next_ts = (seed + 1) * cycle_ms
        next_dt = datetime.datetime.fromtimestamp(next_ts / 1000)
        next_str = f"NEXT: {next_dt.strftime('%H:%M')}"
        d.text((150, 240), next_str, fill="#666666")
        
        # 8. 하단 정보 (회색 작은 글씨)
        d.text((80, 275), "KST Server Time Standard", fill="#999999")

        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', cache_timeout=0)
    except Exception as e:
        return str(e), 500
