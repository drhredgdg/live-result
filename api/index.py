from flask import Flask, send_file
from PIL import Image, ImageDraw
import datetime
import io

app = Flask(__name__)

def calculate_result_by_hashing(seed):
    # game.html의 BigInt 기반 해싱 로직 이식
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
        # 1. 한국 시간 계산 (UTC+9)
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        kst_ts_ms = int(now.timestamp() * 1000)
        
        # 2. 4분 주기 (240,000ms) 시드 계산
        cycle_ms = 4 * 60 * 1000
        seed = kst_ts_ms // cycle_ms
        result_text = calculate_result_by_hashing(seed)
        
        # 3. 이미지 생성 (game.html의 디자인 무드 재현)
        img = Image.new('RGB', (400, 320), color='#f9f9f9')
        d = ImageDraw.Draw(img)
        
        # 4. 중앙 컨테이너 및 파란 테두리 (#4A90E2)
        d.rectangle([20, 20, 380, 300], fill="white", outline="#4A90E2", width=4)
        
        # 5. 헤더 및 결과 디자인
        res_color = "#e74c3c" if result_text == "ODD" else "#337ab7"
        d.text((80, 45), "🎲 YGOSU 4MIN RESULT", fill="#333333")
        
        # 중앙 결과 박스 (큰 글씨 효과 대체)
        d.rectangle([130, 85, 270, 165], fill=res_color)
        d.text((175, 115), result_text, fill="white")
        
        # 6. 타이머 및 시간 정보
        rem_sec = 240 - (int(now.timestamp()) % 240)
        timer_str = f"{rem_sec // 60:02d}:{rem_sec % 60:02d}"
        d.text((175, 185), timer_str, fill="#4A90E2")
        
        next_dt = datetime.datetime.fromtimestamp(((seed + 1) * cycle_ms) / 1000)
        d.text((130, 230), f"NEXT: {next_dt.strftime('%H:%M')}", fill="#666666")
        d.text((90, 275), "SYNCED WITH KST SERVER", fill="#999999")

        # 7. 파일 전송 (에러의 핵심인 max_age로 수정 완료)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Flask 최신 버전에서는 cache_timeout 대신 max_age를 사용합니다.
        return send_file(img_io, mimetype='image/png', max_age=0)
        
    except Exception as e:
        # 에러 발생 시 로그 확인용 텍스트 반환
        return str(e
