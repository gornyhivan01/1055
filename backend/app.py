from flask import Flask, jsonify, request
from celery import Celery
from prometheus_client import Counter, generate_latest
import os

app = Flask(__name__)

# Настройка Celery — только для отправки задач
app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL', 'redis://redis:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('REDIS_URL', 'redis://redis:6379/0')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])

# 🔢 Собственная метрика: число запросов
REQUESTS_COUNTER = Counter('user_requests_total', 'Total number of user requests to /api/check')

@app.route('/api/check', methods=['POST'])
def check():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Увеличиваем счётчик
    REQUESTS_COUNTER.inc()

    # ✅ Отправляем задачу, которую знает worker
    task = celery.send_task('tasks.check_availability', args=[url])

    return jsonify({"task_id": task.id}), 202

@app.route('/api/status/<task_id>')
def status(task_id):
    task = celery.AsyncResult(task_id)
    return jsonify({"status": task.status, "result": task.result}), 200

# 📊 Endpoint для метрик
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4'}

if __name__ == '__main__': # pragma: no cover
    app.run(host='0.0.0.0', port=5000)