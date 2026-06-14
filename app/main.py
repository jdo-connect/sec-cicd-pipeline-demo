from flask import Flask, jsonify
from datetime import datetime, timezone

app = Flask(__name__)

@app.route('/health')
def health():
    timestamp = datetime.now(timezone.utc).isoformat()
    return jsonify({'status': 'ok', 'timestamp': timestamp})


@app.route('/info')
def info():
    return jsonify({'app_name':'sec-cicd-pipeline-demo','version':'1.0.0'})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



