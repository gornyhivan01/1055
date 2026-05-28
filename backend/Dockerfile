FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py /app/app.py

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]