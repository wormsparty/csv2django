#!/bin/sh

cd "$(dirname "$0")"

python3 csv2django.py
python3 csv2test.py

if [ ! -d .venv ]; then
	python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r output/django/requirements.txt

rm -fr output/django/csvdjango output/django/manage.py
django-admin startproject csvdjango output/django
cp output/django/models.py output/django/urls.py output/django/views.py output/django/csvdjango

cat << EOT >> output/django/csvdjango/settings.py
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

cd output/django || exit
mkdir -p csvdjango/migrations
touch csvdjango/migrations/__init__.py
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
