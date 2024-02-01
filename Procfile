web: daphne jusoor_backend.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker --settings=jusoor_backend.settings -v2