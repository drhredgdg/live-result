from flask import Flask, send_file, make_response
from PIL import Image, ImageDraw, ImageFont
import datetime
import io
import os

app = Flask(__name__)

# 업로드한 폰트 파일명과 똑같이 맞춰주세요 (예: NanumGothic-Bold.ttf)
FONT_NAME = "NanumGothic-Bold.ttf"

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
        
        # 이미지 생성 (450x500)
        img = Image.new('RGB', (450, 500), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 1. 디자인 (파란 테두리)
        d.rectangle([40, 40, 410, 460], fill="white", outline="#4A90E2", width=5)
        
        # 2. 폰트 경로 설정
        font_path = os.path.join(os.path.dirname(__file__), FONT_NAME)
        
        try:
            # 폰트가 있으면 한글 출력
            title_f = ImageFont.truetype(font_path, 22)
            result_f = ImageFont.truetype(font_path, 90) # 결과값 크게
            time_f = ImageFont.truetype(font_path, 18)
        except:
            # 폰트 로드 실패 시 에러 방지용 기본 설정
            title_f = result_f = time_f = ImageFont.load_default()

        # 3. 텍스트 그리기
        d.text((125, 80), "와이고수 4분주기 결과", fill="#333333", font=title_f)
        
        # 중앙 결과 (홀/짝)
        res_color = "#e74c3c" if result == "홀" else "#337ab7"
        d.rectangle([140, 140, 310, 260], fill=res_color)
        d.text((180, 155), result, fill="white", font=result_f)
        
        # 시간 및 타이머
        time_str = now.strftime("%Y.%m.%d %H:%M:%S")
        d.text((140, 290), time_label := f"현재시각: {time_str}", fill="#666666", font=time_f)
        
        rem = 240 - (int(now.timestamp()) % 240)
        d.text((165, 335), f"다음 갱신: {rem // 60:02d}:{rem % 60:02d}", fill="#4A90E2", font=time_f)
        d.text((115, 410), "※ 외부 서버(KST) 시간 기준", fill="#bbbbbb", font=time_f)

        # 4. 이미지 바이트 변환 (latin-1 에러 방지 핵심)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # 직접 Response를 만들어 한글 메타데이터가 섞이지 않게 전송
        response = make_response(send_file(img_io, mimetype='image/png'))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
        
    except Exception as e:
        # 에러 발생 시 latin-1 충돌을 피하기 위해 한글 대신 영어로 에러 출력
        return "Internal Error: Check font file or path", 500
