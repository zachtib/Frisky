release: python manage.py migrate
worker: celery worker --app=frisky.celery.app
web: gunicorn app.wsgi