#!/bin/sh

cd "$(dirname "$0")"

python3 main.py

if [ ! -d .venv ]; then
	python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r requirements_django.txt

rm -fr data/django/csvdjango data/django/manage.py
django-admin startproject csvdjango data/django
cp data/django/models.py data/django/urls.py data/django/views.py data/django/csvdjango

cat << EOT >> data/django/csvdjango/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'csvdjango',
]
EOT

cd data/django || exit
mkdir -p csvdjango/migrations
touch csvdjango/migrations/__init__.py
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
