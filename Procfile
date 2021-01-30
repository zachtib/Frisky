release: pip install django-heroku && python manage.py migrate && python manage.py createcachetable
worker: celery -A app worker -l info
web: gunicorn app.wsgi