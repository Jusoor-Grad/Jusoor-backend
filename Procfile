web: daphne jusoor_backend.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A jusoor_backend worker -l INFO