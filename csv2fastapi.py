import csv
from collections import defaultdict

def generate_fastapi_files(csv_file):
    """
    Generates FastAPI models, endpoints, and routers based on a CSV file describing a database schema.

    Parameters:
    csv_file (str): Path to the CSV file containing the database schema description.

    Returns:
    tuple: (models_code, endpoints_code, routers_code)
        models_code (str): Python code for the SQLAlchemy models
        endpoints_code (str): Python code for the FastAPI endpoints
        routers_code (str): Python code for the FastAPI routers
    """
    # Initialize the output strings
    models_code = (
        "from sqlalchemy import Column, Integer, String, Date, ForeignKey\n"
        "from sqlalchemy.ext.declarative import declarative_base\n"
        "from sqlalchemy.orm import relationship\n\n"
        "Base = declarative_base()\n\n"
    )

    endpoints_code = (
        "from fastapi import APIRouter, HTTPException, Depends\n"
        "from sqlalchemy.orm import Session\n"
        "from .models import *\n"
        "from .database import get_db\n"
        "from .schemas import *\n\n"
    )

    schemas_code = (
        "from pydantic import BaseModel\n\n"
    )

    routers_code = (
        "from fastapi import FastAPI\n"
        "from .endpoints import *\n\n"
        "app = FastAPI()\n\n"
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

    # Generate models and schemas
    for table_name, fields in tables.items():
        # Start model class definition
        models_code += f"class {table_name.capitalize()}(Base):\n"
        models_code += f"    __tablename__ = '{table_name.lower()}'\n"

        schemas_code += f"class {table_name.capitalize()}Base(BaseModel):\n"

        # Add fields
        for column_name, column_type in fields:
            if column_type == 'primary_key':
                field = "Column(Integer, primary_key=True, index=True)"
                schema_field = f"{column_name}: int"
            elif column_type == 'string':
                field = "Column(String, index=True)"
                schema_field = f"{column_name}: str"
            elif column_type == 'int':
                field = "Column(Integer)"
                schema_field = f"{column_name}: int"
            elif column_type == 'date':
                field = "Column(Date)"
                schema_field = f"{column_name}: str"
            elif column_type == 'foreign_key':
                referenced_model = column_name.capitalize()
                field = f"Column(Integer, ForeignKey('{referenced_model.lower()}.id'))"
                schema_field = f"{column_name}_id: int"
            else:
                raise ValueError(f"Invalid column type: {column_type}")

            models_code += f"    {column_name} = {field}\n"
            schemas_code += f"    {schema_field}\n"

        # Add relationships if there are foreign keys
        for column_name, column_type in fields:
            if column_type == 'foreign_key':
                referenced_model = column_name.capitalize()
                models_code += f"    {column_name} = relationship('{referenced_model}')\n"

        models_code += "\n"
        schemas_code += "\n"

        # Add schema for creation
        schemas_code += f"class {table_name.capitalize()}Create({table_name.capitalize()}Base):\n    pass\n\n"

        # Add schema for reading
        schemas_code += f"class {table_name.capitalize()}({table_name.capitalize()}Base):\n"
        schemas_code += "    id: int\n\n"
        schemas_code += "    class Config:\n        orm_mode = True\n\n"

    # Generate endpoints and routers
    for table_name in table_names:
        # Generate CRUD endpoints
        endpoint_name = table_name.lower()
        endpoints_code += f"router = APIRouter(prefix='/{endpoint_name}', tags=['{endpoint_name}'])\n\n"

        endpoints_code += f"@router.get('/', response_model=list[{table_name.capitalize()}])\n"
        endpoints_code += f"def read_{endpoint_name}s(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):\n"
        endpoints_code += f"    return db.query({table_name.capitalize()}).offset(skip).limit(limit).all()\n\n"

        endpoints_code += f"@router.post('/', response_model={table_name.capitalize()})\n"
        endpoints_code += f"def create_{endpoint_name}(item: {table_name.capitalize()}Create, db: Session = Depends(get_db)):\n"
        endpoints_code += f"    db_item = {table_name.capitalize()}(**item.dict())\n"
        endpoints_code += f"    db.add(db_item)\n    db.commit()\n    db.refresh(db_item)\n"
        endpoints_code += f"    return db_item\n\n"

        endpoints_code += f"@router.get('/{{item_id}}', response_model={table_name.capitalize()})\n"
        endpoints_code += f"def read_{endpoint_name}(item_id: int, db: Session = Depends(get_db)):\n"
        endpoints_code += f"    item = db.query({table_name.capitalize()}).filter({table_name.capitalize()}.id == item_id).first()\n"
        endpoints_code += f"    if not item:\n        raise HTTPException(status_code=404, detail='{table_name.capitalize()} not found')\n"
        endpoints_code += f"    return item\n\n"

        endpoints_code += f"@router.delete('/{{item_id}}')\n"
        endpoints_code += f"def delete_{endpoint_name}(item_id: int, db: Session = Depends(get_db)):\n"
        endpoints_code += f"    item = db.query({table_name.capitalize()}).filter({table_name.capitalize()}.id == item_id).first()\n"
        endpoints_code += f"    if not item:\n        raise HTTPException(status_code=404, detail='{table_name.capitalize()} not found')\n"
        endpoints_code += f"    db.delete(item)\n    db.commit()\n    return {{'message': 'Deleted successfully'}}\n\n"

        routers_code += f"from .endpoints.{endpoint_name} import router as {endpoint_name}_router\n"
        routers_code += f"app.include_router({endpoint_name}_router)\n\n"

    return models_code, schemas_code, endpoints_code, routers_code

def save_fastapi_files(csv_file, output_dir='.'):
    """
    Generates and saves FastAPI models, endpoints, and routers files.

    Parameters:
    csv_file (str): Path to the CSV file containing the database schema description
    output_dir (str): Directory where the files should be saved
    """
    models_code, schemas_code, endpoints_code, routers_code = generate_fastapi_files(csv_file)

    import os

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save models.py
    with open(os.path.join(output_dir, 'models.py'), 'w') as f:
        f.write(models_code)

    # Save schemas.py
    with open(os.path.join(output_dir, 'schemas.py'), 'w') as f:
        f.write(schemas_code)

    # Save endpoints.py
    with open(os.path.join(output_dir, 'endpoints.py'), 'w') as f:
        f.write(endpoints_code)

    # Save main.py
    with open(os.path.join(output_dir, 'main.py'), 'w') as f:
        f.write(routers_code)

    with open(os.path.join(output_dir, 'requirements.txt'), 'w') as f:
        f.write("fastapi\nsqlalchemy\n")