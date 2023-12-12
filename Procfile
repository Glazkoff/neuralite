release: python manage.py migrate --noinput
web: gunicorn --bind :$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker dtb.asgi:application
worker: celery -A dtb worker -P prefork --loglevel=INFO
beat: celery -A dtb beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
llm-api: gunicorn --bind :9001 --workers 2 --worker-class uvicorn.workers.UvicornWorker llm_api.main:app
langchain: uvicorn langchain_summ.app.server:app --host 0.0.0.0 --port 8080