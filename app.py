from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)
history = []

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8" />
    <title>바카라 패턴 분석 예측기</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 30px; text-align: center; background: #F5F5F5; }
        button { padding: 10px 20px; font-size: 16px; margin: 5px; }
        #history { margin-top: 20px; font-size: 18px; background: white; padding: 10px; }
        #prediction { margin-top: 20px; font-size: 20px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>바카라 패턴 분석 예측기</h1>
    <div>
        <button onclick="sendResult('P')" style="background:#4CAF50;color:white;">플레이어 (P)</button>
        <button onclick="sendResult('B')" style="background:#F44336;color:white;">뱅커 (B)</button>
        <button onclick="sendResult('T')" style="background:#9C27B0;color:white;">타이 (T)</button>
    </div>

    <div id="history">최근 결과: 없음</div>
    <div id="prediction">예측 결과: -</div>
    <button onclick="resetHistory()" style="margin-top:20px; background:#F44336;color:white;">기록 초기화</button>

    <script>
        function sendResult(res) {
            fetch('/add_result', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({result: res})
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('history').innerText = '최근 결과: ' + data.history.join(' ');
                document.getElementById('prediction').innerText = '예측 결과: ' + data.prediction;
            });
        }

        function resetHistory() {
            fetch('/reset', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                document.getElementById('history').innerText = '최근 결과: 없음';
                document.getElementById('prediction').innerText = '예측 결과: -';
            });
        }
    </script>
</body>
</html>
'''

def combined_predict(results):
    player_count = results.count('P')
    banker_count = results.count('B')
    if len(results) < 3:
        return "정보 부족"
    if player_count > banker_count:
        return "다음은 P 가능성 높음 (종합 예측)"
    elif banker_count > player_count:
        return "다음은 B 가능성 높음 (종합 예측)"
    else:
        return "예측 불확실 (종합 예측)"

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/add_result', methods=['POST'])
def add_result():
    global history
    data = request.get_json()
    res = data.get('result', '').upper()
    if res not in ['P', 'B', 'T']:
        return jsonify({"error": "잘못된 입력"}), 400
    history.append(res)
    prediction = combined_predict(history)
    return jsonify({"history": history, "prediction": prediction})

@app.route('/reset', methods=['POST'])
def reset():
    global history
    history = []
    return jsonify({"message": "기록 초기화 완료"})

# Render 환경에서 포트를 열기 위한 설정
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
