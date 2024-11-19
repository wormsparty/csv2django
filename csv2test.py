import csv
from collections import defaultdict
from datetime import date


def generate_tests(csv_file, base_url="http://127.0.0.1:8000"):
    """
    Génère un script de tests Python basé sur un fichier CSV décrivant les entités.
    """
    tables = defaultdict(list)
    dependencies = {}

    # Lecture du CSV et analyse des dépendances
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            table_name = row['table_name']
            column_name = row['column_name']
            column_type = row['column_type']
            tables[table_name].append((column_name, column_type))

            if column_type.startswith('foreign-'):
                if table_name not in dependencies:
                    dependencies[table_name] = set()
                dependencies[table_name].add(column_type.split('-')[1])

    # Tri topologique simple des tables
    table_order = []
    remaining_tables = set(tables.keys())

    while remaining_tables:
        for table in sorted(remaining_tables):
            deps = dependencies.get(table, set())
            if not deps & remaining_tables:
                table_order.append(table)
                remaining_tables.remove(table)
                break

    # Génération des tests
    test_code = (
        "import requests\n"
        "from datetime import date\n"
        "import json\n\n"
        f"BASE_URL = \"{base_url}\"\n\n"
        "def test_api():\n"
        "    created_ids = {}\n\n"
    )

    for table_name in table_order:
        fields = tables[table_name]

        test_code += f"    print('\\nTesting {table_name} endpoints...')\n"
        test_code += f"    response = requests.get(f\"{{BASE_URL}}/{table_name}/\")\n"
        test_code += f"    assert response.status_code == 200, f\"Erreur lors de la récupération des données de {table_name}\"\n"
        test_code += f"    initial_data = response.json()\n"
        test_code += "    initial_count = len(initial_data)\n\n"

        # Création des données du test
        create_data_parts = []
        for column_name, column_type in fields:
            if column_type == "primary_key":
                continue
            elif column_type == "string":
                create_data_parts.append(f"'{column_name}': 'test_{table_name}_{column_name}'")
            elif column_type == "int":
                create_data_parts.append(f"'{column_name}': 25")
            elif column_type == "date":
                create_data_parts.append(f"'{column_name}': str(date.today())")
            elif column_type.startswith("foreign-"):
                related_table = column_type.split('-')[1]
                create_data_parts.append(f"'{column_name}': created_ids['{related_table}']")

        # Création d'une entité avec f-string pour évaluer les références
        test_code += f"    new_{table_name}_data = {{\n        {',\n        '.join(create_data_parts)}\n    }}\n"
        test_code += f"    print(f'Attempting to create {table_name} with data:')\n"
        test_code += f"    print(json.dumps(new_{table_name}_data, indent=2))\n"
        test_code += f"    response = requests.post(f\"{{BASE_URL}}/{table_name}/\", json=new_{table_name}_data)\n"
        test_code += f"    print(f'Response status: {{response.status_code}}')\n"
        test_code += f"    print(f'Response body: {{response.text}}')\n"
        test_code += f"    assert response.status_code == 201, f\"Erreur lors de la création dans {table_name}\"\n"
        test_code += f"    created_item = response.json()\n"
        test_code += f"    created_ids['{table_name}'] = created_item['id']\n\n"

        test_code += f"    response = requests.get(f\"{{BASE_URL}}/{table_name}/\")\n"
        test_code += "    assert response.status_code == 200\n"
        test_code += "    updated_data = response.json()\n"
        test_code += "    assert len(updated_data) == initial_count + 1\n\n"

        test_code += f"    response = requests.get(f\"{{BASE_URL}}/{table_name}/{{created_ids['{table_name}']}}/\")\n"
        test_code += "    assert response.status_code == 200\n"
        test_code += f"    fetched_item = response.json()\n"
        test_code += f"    assert fetched_item['id'] == created_ids['{table_name}']\n\n"

        # Mise à jour avec les mêmes corrections pour les foreign keys
        update_field = next((field_name for field_name, field_type in fields if field_type == "string"), None)

        if update_field:
            update_data_parts = []
            for column_name, column_type in fields:
                if column_type == "primary_key":
                    continue
                elif column_name == update_field:
                    update_data_parts.append(f"'{column_name}': 'updated_{table_name}_{column_name}'")
                elif column_type == "string":
                    update_data_parts.append(f"'{column_name}': 'test_{table_name}_{column_name}'")
                elif column_type == "int":
                    update_data_parts.append(f"'{column_name}': 25")
                elif column_type == "date":
                    update_data_parts.append(f"'{column_name}': str(date.today())")
                elif column_type.startswith("foreign-"):
                    related_table = column_type.split('-')[1]
                    update_data_parts.append(f"'{column_name}': created_ids['{related_table}']")

            test_code += f"    updated_{table_name}_data = {{\n        {',\n        '.join(update_data_parts)}\n    }}\n"
            test_code += f"    response = requests.put(f\"{{BASE_URL}}/{table_name}/{{created_ids['{table_name}']}}/\", json=updated_{table_name}_data)\n"
            test_code += "    assert response.status_code == 200\n"
            test_code += f"    updated_item = response.json()\n"
            test_code += f"    assert updated_item['{update_field}'] == updated_{table_name}_data['{update_field}']\n\n"

    test_code += "    print(\"\\nTous les tests ont réussi!\")\n\n"
    test_code += "if __name__ == \"__main__\":\n"
    test_code += "    test_api()"

    return test_code


def save_test_script(csv_file, output_file='output/test_api.py', base_url="http://127.0.0.1:8000"):
    """
    Génère et enregistre un script de tests basé sur le CSV.
    """
    test_code = generate_tests(csv_file, base_url)
    with open(output_file, 'w') as f:
        f.write(test_code)


if __name__ == '__main__':
    save_test_script("model.csv")