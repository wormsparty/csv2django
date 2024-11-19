import csv
from collections import defaultdict

def generate_django_files(csv_file):
    """
    Generates Django models, views, and URLs based on a CSV file describing a database schema.

    Parameters:
    csv_file (str): Path to the CSV file containing the database schema description.

    Returns:
    tuple: (models_code, views_code, urls_code)
        models_code (str): Python code for the Django models
        views_code (str): Python code for the Django views
        urls_code (str): Python code for the Django URLs
    """
    # Initialize the output strings
    models_code = "from django.db import models\n\n"
    views_code = "from rest_framework import serializers, viewsets\nfrom .models import *\n\n"
    urls_code = (
        "from django.urls import path, include\n"
        "from rest_framework import routers\n"
        "from .views import *\n\n"
    )

    # Group fields by table
    tables = defaultdict(list)
    table_names = set()

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            table_name = row['table_name']
            column_name = row['column_name']
            column_type = row['column_type']
            tables[table_name].append((column_name, column_type))
            table_names.add(table_name)

    # Generate models
    for table_name, fields in tables.items():
        # Start model class definition
        models_code += f"class {table_name.capitalize()}(models.Model):\n"

        # Add fields
        for column_name, column_type in fields:
            if column_type == 'primary_key':
                field = f"models.AutoField(primary_key=True)"
            elif column_type == 'string':
                field = f"models.CharField(max_length=255)"
            elif column_type == 'int':
                field = f"models.IntegerField()"
            elif column_type == 'date':
                field = f"models.DateField()"
            elif column_type.startswith('foreign-'):
                referenced_model = column_type.split('-', 1)[1].capitalize()
                field = f"models.ForeignKey('{referenced_model}', on_delete=models.CASCADE, null=True)"
            else:
                raise ValueError(f"Invalid column type: {column_type}")

            models_code += f"    {column_name} = {field}\n"

        # Add string representation
        models_code += f"\n    def __str__(self):\n        return str(self.id)\n\n"

    # Generate serializers and viewsets
    for table_name in table_names:
        # Generate serializer
        views_code += f"class {table_name.capitalize()}Serializer(serializers.ModelSerializer):\n"
        views_code += "    class Meta:\n"
        views_code += f"        model = {table_name.capitalize()}\n"
        views_code += "        fields = '__all__'\n\n"

        # Generate viewset
        views_code += f"class {table_name.capitalize()}ViewSet(viewsets.ModelViewSet):\n"
        views_code += f"    queryset = {table_name.capitalize()}.objects.all()\n"
        views_code += f"    serializer_class = {table_name.capitalize()}Serializer\n\n"

    # Generate URL configuration
    urls_code += "router = routers.DefaultRouter()\n"
    for table_name in table_names:
        urls_code += f"router.register(r'{table_name.lower()}', {table_name.capitalize()}ViewSet)\n"

    urls_code += "\nurlpatterns = [\n"
    urls_code += "    path('', include(router.urls)),\n"
    urls_code += "    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),\n"
    urls_code += "]\n"

    return models_code, views_code, urls_code

if __name__ == "__main__":
    csv_file = 'model.csv'
    output_dir = 'output/django'

    models_code, views_code, urls_code = generate_django_files(csv_file)

    import os

    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'models.py'), 'w') as f:
        f.write(models_code)

    with open(os.path.join(output_dir, 'views.py'), 'w') as f:
        f.write(views_code)

    with open(os.path.join(output_dir, 'urls.py'), 'w') as f:
        f.write(urls_code)

    with open(os.path.join(output_dir, 'requirements.txt'), 'w') as f:
        f.write("django\ndjango_rest_framework\nrequests\n")