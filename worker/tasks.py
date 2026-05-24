import requests
from celery import Celery
import os
import socket
from urllib.parse import urlparse

celery = Celery('tasks', broker=os.getenv('REDIS_URL'), backend=os.getenv('REDIS_URL'))

@celery.task(name='tasks.check_availability')
def check_availability(url):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.hostname

        # Получаем IP по домену
        ip = socket.gethostbyname(domain)

        response = requests.get(url, timeout=10)
        return {
            "url": url,
            "ip": ip,
            "status": response.status_code,
            "online": True
        }
    except socket.gaierror as e:
        return {
            "url": url,
            "online": False,
            "error": f"Could not resolve IP: {str(e)}"
        }
    except requests.RequestException as e:
        return {
            "url": url,
            "online": False,
            "error": str(e)
        }