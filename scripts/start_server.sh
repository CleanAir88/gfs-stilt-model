#!/bin/bash

service redis-server start

python manage.py makemigrations
python manage.py migrate

echo "import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model();print('Superuser already exists.' if User.objects.filter(username='admin').exists() else (User.objects.create_superuser('admin', '', 'admin123456'), print('Superuser created.')))" | python manage.py shell

python manage.py runserver 0.0.0.0:8000 &

# celery worker
celery -A server worker -Q gfs_stilt --concurrency=1 --hostname=gfs_stilt_worker@%h &

# celery beat
celery -A server beat --loglevel=info &

# flower
celery -A server flower --port=5555 --basic_auth=flower:flower123456 &

wait
