import csv2django
import csv2fastapi

csv2django.save_django_files('data/model.csv', 'data/django')
csv2fastapi.save_fastapi_files('data/model.csv', 'data/fastapi')
