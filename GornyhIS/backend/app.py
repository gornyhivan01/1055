# backend/app.py
from flask import Flask, request, jsonify
from celery import Celery
import os

app = Flask(__name__)
celery = Celery('tasks', broker=os.getenv('REDIS_URL'), backend=os.getenv('REDIS_URL'))

@app.route('/api/check', methods=['POST'])
def check_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    task = celery.send_task('tasks.check_availability', args=[data['url']])
    return jsonify({"task_id": task.id}), 202

@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    res = celery.AsyncResult(task_id)
    response_data = {"status": res.status}

    if res.ready():
        result = res.result
        # Передаём весь результат, включая URL, IP, статус и online
        response_data["result"] = result
    else:
        response_data["result"] = None  # или можно добавить "processing"

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)