from flask import Flask, send_file
from PIL import Image, ImageDraw, ImageFont # ImageFont 추가
import datetime
import io
import os

app = Flask(__name__)

def calculate_result(seed):
    hash_val = int(seed) * 16777619
    hash_val = (hash_val ^ (hash_val >> 13)) * 131
    hash_val = (hash_val ^ (hash_val >> 15))
    last_char = hex(hash_val)[-1]
    try:
        digit = int(last_char, 16)
    except:
        digit = 0
    return "홀" if digit % 2 != 0 else "짝"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    try:
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        seed = int(now.timestamp()) // 240
        result = calculate_result(seed)
        
        img = Image.new('RGB', (450, 520), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 1. 디자인: 파란 테두리
        d.rectangle([40, 40, 410, 480], outline="#4A90E2", width=5)
        
        # 2. 폰트 설정 (api 폴더 내 NanumGothic.ttf가 있다고 가정)
        # 폰트 파일이 없을 경우를 대비해 에러 처리를 합니다.
        font_path = os.path.join(os.path.dirname(__file__), "NanumGothic.ttf")
        
        try:
            # 결과값 폰트 (크게)
            result_font = ImageFont.truetype(font_path, 60)
            # 일반 텍스트 폰트 (작게)
            main_font = ImageFont.truetype(font_path, 20)
        except:
            # 폰트 파일이 없으면 기본 폰트로 복귀 (이 경우 다시 에러가 날 수 있음)
            result_font = ImageFont.load_default()
            main_font = ImageFont.load_default()

        # 3. 제목
        d.text((130, 80), "와이고수 4분주기 결과", fill="#333333", font=main_font)
        
        # 4. 결과 박스 및 한글 출력
        res_color = "#e74c3c" if result == "홀" else "#337ab7"
        d.rectangle([140, 140, 310, 250], fill=res_color)
        
        # 한글 '홀' 또는 '짝' 출력 (중앙 정렬을 위해 좌표 조정)
        d.text((195, 160), result, fill="white", font=result_font)
        
        # 5. 시간 및 타이머
        d.text((150, 270), now.strftime("%y.%m.%d %H:%M:%S"), fill="#666666", font=main_font)
        
        rem = 240 - (int(now.timestamp()) % 240)
        timer_str = f"남은시간: {rem // 60:02d}:{rem % 60:02d}"
        d.text((170, 320), timer_str, fill="#4A90E2", font=main_font)
        
        # 6. 하단 안내
        d.text((120, 410), "KST 서버 시간 기준 (4분 주기)", fill="#cccccc", font=main_font)

        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', max_age=0)
        
    except Exception as e:
        # 에러 발생 시 latin-1 에러를 피하기 위해 영문으로 에러 출력
        return "Error occurred. Check font file.", 500
