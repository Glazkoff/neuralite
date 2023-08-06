release: python manage.py migrate --noinput
web: gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker dtb.asgi:application
worker: celery -A dtb worker -P prefork --loglevel=INFO
beat: celery -A dtb beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
llm-api: uvicorn llm_api.main:app --reload --host 0.0.0.0 --port $PORT --workers 4
