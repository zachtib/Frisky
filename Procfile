release: python manage.py migrate
worker: celery -A app worker -l info
web: gunicorn app.wsgi