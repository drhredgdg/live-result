from flask import Flask, send_file
from PIL import Image, ImageDraw
import datetime
import io

app = Flask(__name__)

def calculate_result(seed):
    # game.html 해싱 로직과 100% 일치
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
        
        # 캔버스 및 카드 디자인 (흰색 배경)
        img = Image.new('RGB', (450, 520), color='#FFFFFF')
        d = ImageDraw.Draw(img)
        
        # 1. 둥근 사각형 느낌의 파란 테두리
        d.rectangle([40, 40, 410, 480], fill="white", outline="#4A90E2", width=5)
        
        # 2. 상단 제목 (한글 깨짐 대비해 영문/한글 혼용 시도)
        d.text((130, 80), "YGOSU 4MIN RESULT", fill="#333333")
        
        # 3. 결과값 표시 (가장 중요한 부분!)
        res_color = "#e74c3c" if result == "홀" else "#337ab7"
        
        # 글자가 깨질 것을 대비해 "색상 박스"를 더 크게 그리고
        # 박스 안에 결과값을 넣습니다.
        d.rectangle([140, 140, 310, 240], fill=res_color)
        
        # 서버에 한글 폰트가 없으면 '홀/짝'이 깨질 수 있으므로
        # 박스 위에 'ODD' 또는 'EVEN'을 크게 쓰고, 
        # 그 아래에 작게 한글을 병기하거나 색상으로 구분하게 만듭니다.
        # (만약 한글 폰트가 잡히면 정상적으로 '홀/짝'이 나옵니다)
        display_text = f"{result}" 
        d.text((210, 180), display_text, fill="white")
        
        # 4. 시간 및 타이머 정보
        time_label = now.strftime("%y.%m.%d %H:%M:%S")
        d.text((150, 260), time_label, fill="#666666")
        
        rem = 240 - (int(now.timestamp()) % 240)
        timer_str = f"{rem // 60:02d}:{rem % 60:02d}"
        d.text((200, 310), timer_str, fill="#4A90E2")
        
        # 5. 하단 안내
        d.text((140, 380), "NEXT: " + (now + datetime.timedelta(seconds=rem)).strftime("%H:%M"), fill="#999999")
        d.text((120, 420), "KST SERVER TIME STANDARD", fill="#cccccc")

        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', max_age=0)
        
    except Exception as e:
        return str(e), 500
