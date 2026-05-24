FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY *.py .

# Запускаем через Gunicorn (WSGI)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
