from flask import Flask, send_file
from PIL import Image, ImageDraw
import datetime
import io

app = Flask(__name__)

def calculate_result_by_hashing(seed):
    # JavaScript의 BigInt(seed) * 16777619n 로직 재현
    # 파이썬은 정수 크기에 제한이 없으므로 n을 붙이지 않습니다.
    hash_val = int(seed) * 16777619
    hash_val = (hash_val ^ (hash_val >> 13)) * 131
    hash_val = (hash_val ^ (hash_val >> 15))
    
    # 마지막 16진수 자리 추출
    hex_str = hex(hash_val).upper()
    last_char = hex_str[-1]
    
    try:
        last_digit = int(last_char, 16)
    except:
        last_digit = 0
        
    return "홀" if last_digit % 2 != 0 else "짝"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_result(path):
    try:
        # 1. 한국 시간 설정
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        kst_timestamp_ms = int(now.timestamp() * 1000)
        
        # 2. 4분 주기 (240,000ms)
        cycle_duration_ms = 4 * 60 * 1000
        current_seed = kst_timestamp_ms // cycle_duration_ms
        
        # 3. 결과 계산
        result = calculate_result_by_hashing(current_seed)
        
        # 4. 이미지 생성 (디자인)
        img = Image.new('RGB', (400, 300), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 테두리
        d.rectangle([5, 5, 395, 295], outline="#4A90E2", width=5)
        
        # 텍스트 출력 (폰트 경로 에러 방지를 위해 기본 폰트 사용)
        res_color = "#e74c3c" if result == "홀" else "#337ab7"
        d.text((100, 40), "🎲 YGOSU 4MIN ODD/EVEN", fill="#333333")
        d.text((180, 100), result, fill=res_color)
        
        # 타이머 및 시간
        remaining = 240 - (int(now.timestamp()) % 240)
        timer_str = f"{remaining // 60:02d}:{remaining % 60:02d}"
        d.text((170, 160), timer_str, fill="#4A90E2")
        d.text((120, 220), f"TIME: {now.strftime('%H:%M:%S')}", fill="#888888")

        # 5. 전송
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        # 에러 발생 시 텍스트로 에러 출력 (디버깅용)
        return str(e), 500
