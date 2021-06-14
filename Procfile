release: python manage.py migrate && python manage.py createcachetable
web: gunicorn app.wsgi --log-file -