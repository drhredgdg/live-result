<!DOCTYPE html>
<html>
<head>
    <title>API 동기화 홀짝 결과 표시기</title>
    <meta charset="UTF-8">
    <style>
        /* ------------------ 스타일 (CSS) ------------------ */
        body { margin: 0; padding: 0; background-color: #f9f9f9; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; }
        #result-container {
            border: 3px solid #4A90E2;
            padding: 30px 40px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            max-width: 400px; 
            background-color: white;
        }
        .header { font-size: 22px; font-weight: bold; color: #333; margin-bottom: 20px; }
        #currentResult { 
            font-size: 70px; 
            font-weight: bold; 
            margin: 10px 0;
            transition: color 0.5s ease-in-out;
            display: block; 
        }
        .odd { color: #e74c3c; /* 홀수: 빨강 */ }
        .even { color: #337ab7; /* 짝수: 파랑 */ }
        .time-label { 
            display: block; 
            font-size: 24px; 
            font-weight: normal;
            color: #666;
            margin-top: -10px; 
        }
        #timer { font-size: 36px; font-weight: bold; color: #4A90E2; margin-top: 15px; margin-bottom: 10px; }
        #nextCycle { font-size: 16px; color: #666; }
        .info { font-size: 14px; color: #999; margin-top: 20px; }
        /* ------------------------------------------------ */
    </style>
</head>
<body>
<div id="result-container">
    <div class="header">🎲 와이고수 4분주기 홀짝 결과</div>
    <div id="currentResult" class="odd">
        -
        <span id="resultTime" class="time-label">-</span>
    </div>
    <div id="timer">로딩 중...</div>
    <div id="nextCycle"></div>
    <div class="info">※ 이 결과는 외부 서버 시간(KST)을 기준으로 합니다.</div>
</div>

<script>
// JavaScript 로직 (API 기반 동기화 계산)
const CYCLE_DURATION_MS = 4 * 60 * 1000; // 4분 주기
const API_URL = 'https://worldtimeapi.org/api/timezone/Asia/Seoul';

let nextCycleTimer;
let timeGap = 0; // 서버 시간과 로컬 시간의 차이 (밀리초)
let lastApiUpdateTime = 0; // 마지막으로 API 시간을 받은 로컬 시간

// 🔴 난수 생성기 대체: 시드 해싱 기반 결과 결정 함수
function calculateResultByHashing(seed) {
    // 시드를 문자열로 변환하여 간단한 해싱(숫자열 조합)을 수행합니다.
    // 이는 시드가 조금만 바뀌어도 출력 결과(Hash)가 크게 바뀌는 효과를 시뮬레이션합니다.
    
    // 1. 시드에 큰 소수를 곱하여 복잡성을 높입니다.
    // BigInt를 사용하여 큰 숫자를 다룹니다.
    let hash = BigInt(seed) * 16777619n;
    
    // 2. 여러 번의 XOR 연산과 시프트 연산을 통해 해싱합니다.
    hash = (hash ^ (hash >> 13n)) * 131n;
    hash = (hash ^ (hash >> 15n));
    
    // 3. 최종 해시값을 16진수 문자열로 변환합니다.
    const hex = hash.toString(16).toUpperCase();
    
    // 4. 16진수 결과의 '마지막 자리 숫자'를 추출하여 홀/짝을 결정합니다.
    // 16진수 A~F(10~15)도 숫자로 간주합니다.
    const lastChar = hex.slice(-1); 
    const lastDigit = parseInt(lastChar, 16); 

    const isOdd = lastDigit % 2 !== 0;
    const result = isOdd ? '홀' : '짝';

    // (디버깅 용도: 콘솔에 시드와 최종 숫자 표시)
    // console.log(`Seed: ${seed}, Last Hex: ${lastChar}, Last Digit: ${lastDigit}, Result: ${result}`);
    
    return result;
}

// 🔴 외부 API (WorldTimeAPI)를 통해 현재 KST 시간을 가져오고 timeGap을 계산
async function calculateTimeGap() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('API 응답 실패');
        
        const data = await response.json();
        const serverTimeMs = new Date(data.datetime).getTime(); 
        const nowLocalTimeMs = new Date().getTime();
        
        timeGap = serverTimeMs - nowLocalTimeMs;
        lastApiUpdateTime = nowLocalTimeMs;
        
        return serverTimeMs;

    } catch (e) {
        console.error("Time API 호출 오류 발생: 로컬 시간으로 대체합니다.", e);
        timeGap = 0;
        lastApiUpdateTime = new Date().getTime();
        
        const now = new Date();
        const KST_OFFSET_MS = 9 * 60 * 60 * 1000;
        const utcTime = now.getTime() + (now.getTimezoneOffset() * 60 * 1000);
        return utcTime + KST_OFFSET_MS;
    }
}

// 🔴 보정된 KST 시간을 얻는 함수
function getCorrectedKSTTime(nowLocalTimeMs) {
    return nowLocalTimeMs + timeGap;
}


// 시간 동기화 및 결과 계산 (TimeGap 사용)
function getSynchronizedResult(kstTime) {
    const currentSeed = Math.floor(kstTime / CYCLE_DURATION_MS);
    
    // 현재 회차 시작 시각 계산 (4분 주기의 시작 시점)
    const currentCycleStartTimeMs = currentSeed * CYCLE_DURATION_MS;
    const currentCycleStartTime = new Date(currentCycleStartTimeMs);

    const nextCycleTimeMs = (currentSeed + 1) * CYCLE_DURATION_MS;
    const nextCycleDate = new Date(nextCycleTimeMs);
    
    // 🔴 수정된 함수 호출: 시드 해싱 기반 결과 결정
    const result = calculateResultByHashing(currentSeed);

    // 표시할 시각 포맷
    const timeDisplay = currentCycleStartTime.toLocaleTimeString('ko-KR', {
        year: '2-digit', month: '2-digit', day: '2-digit', 
        hour: '2-digit', minute: '2-digit', hour12: false, 
        timeZone: 'Asia/Seoul'
    }).replace(/\.\s/g, '.').replace(' ', ' ');

    return { 
        nextCycleTime: nextCycleDate, 
        result, 
        timeDisplay,
        kstTime 
    };
}

// UI 업데이트
async function updateDisplay() {
    const nowLocalTimeMs = new Date().getTime();
    
    const API_REFRESH_INTERVAL = 5000;
    if (nowLocalTimeMs - lastApiUpdateTime >= API_REFRESH_INTERVAL || lastApiUpdateTime === 0) {
        await calculateTimeGap(); 
    }

    const kstTime = getCorrectedKSTTime(nowLocalTimeMs);
    const { nextCycleTime, result, timeDisplay } = getSynchronizedResult(kstTime);

    const diffMs = nextCycleTime.getTime() - kstTime;
    
    if (diffMs <= 0) {
        initResultDisplay(); 
        return;
    }

    const minutes = Math.floor(diffMs / (60 * 1000));
    const seconds = Math.floor((diffMs % (60 * 1000)) / 1000);

    const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    const resultDiv = document.getElementById('currentResult');
    const timeLabelDiv = document.getElementById('resultTime');
    const timerDiv = document.getElementById('timer');
    const cycleDiv = document.getElementById('nextCycle');

    resultDiv.firstChild.textContent = result;
    resultDiv.className = result === '홀' ? 'odd' : 'even';
    
    timeLabelDiv.textContent = timeDisplay;
    
    timerDiv.textContent = timeString;
    cycleDiv.textContent = 
        `다음 결과 변경 시각: ${nextCycleTime.toLocaleTimeString('ko-KR', { timeZone: 'Asia/Seoul', hour: '2-digit', minute: '2-digit' })}`;
}

// 초기화
function initResultDisplay() {
    if (nextCycleTimer) {
        clearInterval(nextCycleTimer);
    }
    
    nextCycleTimer = setInterval(updateDisplay, 1000);
    updateDisplay();
}

window.onload = initResultDisplay;
</script>
</body>
</html>
