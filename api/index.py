from flask import Flask, send_file
from PIL import Image, ImageDraw, ImageFont
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
        
        # 이미지 생성 (원본 사이트 느낌의 450x500)
        img = Image.new('RGB', (450, 500), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 디자인: 파란 테두리 및 그림자
        d.rectangle([45, 45, 415, 465], outline="#eeeeee", width=5)
        d.rectangle([40, 40, 410, 460], fill="white", outline="#4A90E2", width=4)
        
        # 폰트 로드 (api 폴더 내 NanumGothic.ttf 사용)
        base_path = os.path.dirname(__file__)
        font_path = os.path.join(base_path, "NanumGothic.ttf")
        
        try:
            title_f = ImageFont.truetype(font_path, 20)
            result_f = ImageFont.truetype(font_path, 80) # 홀/짝을 아주 크게
            info_f = ImageFont.truetype(font_path, 16)
        except:
            # 폰트 로드 실패 시 에러가 나지 않도록 기본 폰트 사용
            title_f = result_f = info_f = ImageFont.load_default()

        # 1. 상단 제목
        d.text((120, 80), "와이고수 4분주기 결과", fill="#333333", font=title_f)
        
        # 2. 결과 박스 및 홀/짝 (중앙 배치)
        res_color = "#e74c3c" if result == "홀" else "#337ab7"
        d.rectangle([145, 130, 305, 250], fill=res_color)
        d.text((185, 145), result, fill="white", font=result_f)
        
        # 3. 시간 및 타이머
        time_str = now.strftime("%Y.%m.%d %H:%M:%S")
        d.text((145, 280), time_str, fill="#666666", font=info_f)
        
        rem = 240 - (int(now.timestamp()) % 240)
        timer_str = f"다음 갱신까지 {rem // 60:02d}:{rem % 60:02d}"
        d.text((160, 330), timer_str, fill="#4A90E2", font=info_f)
        
        # 4. 하단 안내
        d.text((115, 400), "※ 외부 서버(KST) 시간과 동기화됨", fill="#bbbbbb", font=info_f)

        # 5. 핵심: 에러 방지를 위해 이미지 바이너리만 추출
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # 'latin-1' 에러를 피하기 위해 response headers에 직접 관여하지 않고 전송
        return send_file(img_io, mimetype='image/png', max_age=0)
        
    except Exception as e:
        # 에러 발생 시 영어로만 출력 (latin-1 에러 방지)
        return "Internal Server Error", 500
