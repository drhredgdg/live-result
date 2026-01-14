from flask import Flask, send_file
from PIL import Image, ImageDraw
import datetime
import io

app = Flask(__name__)

def calculate_result(seed):
    # game.html의 해싱 로직 (BigInt 대응)
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
        # 1. 한국 시간 계산
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        seed = int(now.timestamp()) // 240
        result = calculate_result(seed)
        
        # 2. 이미지 생성 (원본 사이트와 비슷한 500x500 사이즈)
        img = Image.new('RGB', (500, 500), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 3. 디자인 재현 (그림자 효과 및 라운드 테두리 대용 사각형)
        # 그림자 레이어
        d.rectangle([55, 55, 445, 445], fill="#f0f0f0") 
        # 메인 카드 (파란색 테두리: #4A90E2)
        d.rectangle([50, 50, 440, 440], fill="white", outline="#4A90E2", width=4)
        
        # 4. 텍스트 배치 (에러 원인인 이모지 🎲 삭제)
        # 제목
        d.text((150, 80), "YGOSU 4MIN ODD-EVEN", fill="#333333")
        
        # 결과값 강조 (홀/짝 색상)
        res_color = "#e74c3c" if result == "ODD" else "#337ab7"
        # 중앙 큰 박스
        d.rectangle([150, 140, 350, 240], fill=res_color)
        # 결과 글자 (서버 한글 깨짐 방지를 위해 영어 사용)
        d.text((220, 180), result, fill="white")
        
        # 5. 시간 정보 (원본 형식: 26.01.15.02:16)
        time_label = now.strftime("%y.%m.%d.%H:%M")
        d.text((195, 260), time_label, fill="#666666")
        
        # 6. 타이머 (가운데 정렬 느낌)
        rem = 240 - (int(now.timestamp()) % 240)
        timer_str = f"{rem // 60:02d}:{rem % 60:02d}"
        d.text((230, 310), timer_str, fill="#4A90E2")
        
        # 7. 하단 설명
        d.text((160, 360), f"NEXT CHANGE: { (now + datetime.timedelta(seconds=rem)).strftime('%H:%M') }", fill="#999999")
        d.text((120, 400), "KST SERVER TIME STANDARD", fill="#cccccc")

        # 8. 이미지 전송 (에러 방지를 위해 BytesIO 사용)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # max_age=0으로 실시간 갱신 처리
        return send_file(img_io, mimetype='image/png', max_age=0)
        
    except Exception as e:
        # 에러 발생 시 텍스트로 표시
        return str(e), 500
