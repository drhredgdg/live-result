from flask import Flask, Response
from PIL import Image, ImageDraw, ImageFont
import datetime
import io
import os

app = Flask(__name__)

# 폰트 파일명 (GitHub에 올린 이름과 대소문자까지 똑같아야 함)
FONT_NAME = "NanumGothic-Bold.ttf"

def calculate_result(seed):
    hash_val = int(seed) * 16777619
    hash_val = (hash_val ^ (hash_val >> 13)) * 131
    hash_val = (hash_val ^ (hash_val >> 15))
    last_digit = int(hex(hash_val)[-1], 16)
    return "홀" if last_digit % 2 != 0 else "짝"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    try:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        seed = int(now.timestamp()) // 240
        result = calculate_result(seed)
        
        # 1. 이미지 생성
        img = Image.new('RGB', (450, 500), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 2. 테두리 및 배경
        d.rectangle([40, 40, 410, 460], outline="#4A90E2", width=5)
        
        # 3. 폰트 로드
        font_path = os.path.join(os.path.dirname(__file__), FONT_NAME)
        try:
            # 폰트 크기를 game.html 느낌으로 크게 조정
            title_f = ImageFont.truetype(font_path, 20)
            result_f = ImageFont.truetype(font_path, 100)
            info_f = ImageFont.truetype(font_path, 16)
        except:
            title_f = result_f = info_f = ImageFont.load_default()

        # 4. 텍스트 그리기
        d.text((130, 80), "YGOSU 4MIN RESULT", fill="#333333", font=title_f)
        
        # 결과 박스
        res_color = "#E74C3C" if result == "홀" else "#337AB7"
        d.rectangle([140, 130, 310, 250], fill=res_color)
        # 결과 한글 (이건 이미지 위에 그려지는 거라 안전함)
        d.text((180, 140), result, fill="white", font=result_f)
        
        # 시간 및 타이머
        d.text((140, 280), now.strftime("%Y.%m.%d %H:%M:%S"), fill="#666666", font=info_f)
        
        rem = 240 - (int(now.timestamp()) % 240)
        timer_str = f"NEXT: {rem // 60:02d}:{rem % 60:02d}"
        d.text((180, 320), timer_str, fill="#4A90E2", font=info_f)
        d.text((120, 410), "SYNCED WITH KST SERVER TIME", fill="#BBBBBB", font=info_f)

        # 5. [핵심] 이미지 바이너리 추출
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # 6. [해결책] 한글 텍스트 없이 순수 이미지 데이터만 Response로 반환
        return Response(img_io.getvalue(), mimetype='image/png', headers={
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'
        })
        
    except Exception as e:
        # 에러 발생 시 영문으로만 리턴해서 latin-1 에러 방지
        return f"Error: {str(e)}", 500
