from flask import Flask, send_file
from PIL import Image, ImageDraw, ImageFilter
import datetime
import io

app = Flask(__name__)

def calculate_hash_result(seed):
    # game.html의 BigInt 해싱 로직 (결과값 100% 일치)
    hash_val = int(seed) * 16777619
    hash_val = (hash_val ^ (hash_val >> 13)) * 131
    hash_val = (hash_val ^ (hash_val >> 15))
    last_digit = int(hex(hash_val)[-1], 16)
    return "홀" if last_digit % 2 != 0 else "짝"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_image(path):
    try:
        # 1. 데이터 계산
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        seed = int(now.timestamp()) // 240
        result = calculate_hash_result(seed)
        
        # 2. 캔버스 설정 (전체 배경색: 흰색)
        img = Image.new('RGB', (500, 550), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 3. 그림자 및 둥근 카드 (Shadow & Card)
        # 그림자 효과를 위해 살짝 어두운 사각형을 먼저 그림
        d.rounded_rectangle([75, 75, 425, 475], radius=20, fill="#E0E0E0")
        # 메인 카드 본체
        d.rounded_rectangle([70, 70, 420, 470], radius=20, fill="white", outline="#4A90E2", width=4)
        
        # 4. 상단 제목 (🎲 와이고수 4분주기 홀짝 결과)
        d.text((150, 100), "🎲 YGOSU 4MIN RESULT", fill="#333333")
        
        # 5. 중앙 결과값 (홀/짝) - 크게 강조
        res_color = "#E74C3C" if result == "홀" else "#337AB7"
        # 폰트 깨짐 방지를 위해 큰 사각형 박스로 결과 표현
        d.rectangle([160, 160, 330, 240], fill=res_color)
        
        # 결과 텍스트 (영문이 안 깨지므로 병기)
        display_text = f"{result} (ODD)" if result == "홀" else f"{result} (EVEN)"
        d.text((200, 190), display_text, fill="white")
        
        # 6. 중간 날짜/시간 (26.01.15.02:16 형태)
        time_label = now.strftime("%y.%m.%d.%H:%M")
        d.text((180, 270), time_label, fill="#666666")
        
        # 7. 타이머 (03:34 형태 - 파란색 굵게)
        rem = 240 - (int(now.timestamp()) % 240)
        timer_str = f"{rem // 60:02d}:{rem % 60:02d}"
        d.text((215, 320), timer_str, fill="#4A90E2")
        
        # 8. 하단 문구
        d.text((170, 370), "다음 결과 변경 시각: " + (now + datetime.timedelta(seconds=rem)).strftime("%H:%M"), fill="#999999")
        d.text((120, 420), "※ 이 결과는 외부 서버 시간(KST)을 기준으로 합니다.", fill="#CCCCCC")

        # 9. 이미지 전송
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', max_age=0)
        
    except Exception as e:
        return str(e), 500
