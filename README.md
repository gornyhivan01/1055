
# 🌐 URL Checker (Microservices Project)

[![CI/CD Pipeline](https://github.com)](https://github.com)

Сервис для проверки доступности веб-сайтов, построенный на микросервисной архитектуре с использованием Docker.

## 🏗 Архитектура системы

Проект разделен на независимые слои для обеспечения отказоустойчивости и возможности масштабирования.

```mermaid
graph TD
    User((Пользователь)) -->|HTTP:80| Nginx[Nginx Gateway]
    
    subgraph "Frontend Layer"
        Nginx -->|Static HTML/JS| FE[Frontend Container]
    end

    subgraph "Backend Layer"
        Nginx -->|/api/*| BE[Backend Flask API]
        BE -->|Отправка задачи| Redis[(Redis Broker)]
    end

    subgraph "Worker Layer (Long Task Processor)"
        Worker[Celery Worker] -->|Слушает очередь| Redis
        Worker -->|Проверка URL| Internet((Internet))
        Internet -.->|Результат| Worker
        Worker -->|Запись результата| Redis
    end

    BE -.->|Опрос статуса| Redis
```

## 🛠 Технологический стек
- Gateway: Nginx (Reverse Proxy)
- Frontend: HTML5 / JavaScript (Vanilla) / Nginx
- Backend: Python 3.11 / Flask / Gunicorn (WSGI)
- Task Queue: Celery + Redis
- Worker: Python 3.11 / Requests
- Orchestration: Docker Compose

## 🚀 Быстрый запуск
Все компоненты запускаются одной командой из корневой директории `GornyhIS`

```bash
docker compose up --build
```

После запуска приложение доступно по адресу: 
```text
http://localhost
```

## 📂 Структура проекта
```text
/backend — API для приема заявок и отдачи статуса задач.
/worker — Сервис, выполняющий реальные HTTP-запросы.
/frontend — Простой UI для взаимодействия с пользователем.
nginx.conf — Правила маршрутизации трафика.
docker-compose.yml — Описание связи всех контейнеров.
```
## ✨ Особенности реализации
- **Выбор протокола**: пользователь выбирает `http://` или `https://` через выпадающий список.
- **Определение IP**: при проверке сайта автоматически определяется IP-адрес сервера через DNS.
- **Отображение результата**: на экран выводится:
  - Статус доступности (✅/❌)
  - HTTP-статус код
  - IP-адрес целевого сервера
- **Асинхронная обработка**:
  - Задача отправляется в очередь через Redis
  - Backend сразу возвращает `task_id`
  - Frontend опрашивает статус через polling

## 📝 Как это работает
1. Пользователь выбирает протокол (`http` или `https`) и вводит домен (например, `google.com`).
2. Frontend формирует полный URL и отправляет POST-запрос на `/api/check`.
3. Backend создаёт задачу в Celery, возвращает `task_id`.
4. Celery Worker забирает задачу, определяет IP-адрес, делает HTTP-запрос.
5. Результат сохраняется в Redis.
6. Frontend периодически опрашивает `/api/status/<task_id>`, пока не получит результат.
7. Отображается статус, код ответа и IP-адрес.

## ✅ Тестирование
Юнит-тесты Worker:
```bash 
cd worker 
python -m pytest test_tasks.py -v --cov=tasks --cov-report=term
```

Тесты проверяют:
- Успешный ответ с IP
- Ошибку DNS (неизвестный хост)
- Ошибку подключения (таймаут, отказ соединения)

Юнит-тесты Backend:
```bash 
cd backend 
python -m pytest test_app.py -v
```
- Он проверяет корректность HTTP-маршрутов и взаимодействие с Celery
- не запускает реальных задач

---

Проект полностью рабочий, модульный и готов к демонстрации 💯
