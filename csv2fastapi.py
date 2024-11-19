import csv
from collections import defaultdict
import os

def generate_fastapi_files_with_database(csv_file):
    """
    Generates FastAPI models, schemas, endpoints, and database configuration for a modular FastAPI application.

    Parameters:
    csv_file (str): Path to the CSV file containing the database schema description.

    Returns:
    tuple: (models_code, schemas_code, endpoint_files, database_code, init_code, main_code)
    """
    # Initialize the output strings
    models_code = (
        "from sqlalchemy import Column, Integer, String, Date, ForeignKey\n"
        "from sqlalchemy.ext.declarative import declarative_base\n"
        "from sqlalchemy.orm import relationship\n\n"
        "Base = declarative_base()\n\n"
    )

    schemas_code = (
        "from pydantic import BaseModel\n\n"
    )

    main_code = (
        "from fastapi import FastAPI\n"
        "from .endpoints import routers\n"
        "from .database import create_tables\n\n"
        "app = FastAPI()\n"
        "create_tables()\n\n"
        "# Include all routers\n"
        "for router in routers:\n"
        "    app.include_router(router)\n\n"
        "@app.get('/')\n"
        "def root():\n"
        "    return {'message': 'Welcome to the API'}\n"
    )

    database_code = (
        "from sqlalchemy import create_engine\n"
        "from sqlalchemy.orm import sessionmaker\n\n"
        "from .models import Base\n"
        "SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'\n\n"
        "# Connect to the database\n"
        "engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})\n"
        "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n\n"
        "def get_db():\n"
        "    db = SessionLocal()\n"
        "    try:\n"
        "        yield db\n"
        "    finally:\n"
        "        db.close()\n\n"
        "def create_tables():\n"
        "    Base.metadata.create_all(bind=engine)\n"
    )

    endpoint_files = {}
    init_code = ""

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
            elif column_type.startswith('foreign-'):
                referenced_table = column_type.split('-', 1)[1]
                field = f"Column(Integer, ForeignKey('{referenced_table.lower()}.id'))"
                schema_field = f"{column_name}_id: int"
            else:
                raise ValueError(f"Invalid column type: {column_type}")

            models_code += f"    {column_name} = {field}\n"
            schemas_code += f"    {schema_field}\n"

        models_code += "\n"
        schemas_code += "\n"

        # Add schema for creation
        schemas_code += f"class {table_name.capitalize()}Create({table_name.capitalize()}Base):\n    pass\n\n"

        # Add schema for reading
        schemas_code += f"class {table_name.capitalize()}({table_name.capitalize()}Base):\n"
        schemas_code += "    id: int\n\n"
        schemas_code += "    class Config:\n        orm_mode = True\n\n"

        # Generate endpoint for this table
        endpoint_code = (
            f"from fastapi import APIRouter, HTTPException, Depends\n"
            f"from sqlalchemy.orm import Session\n"
            f"from ..models import {table_name.capitalize()} as {table_name.capitalize()}Model\n"
            f"from ..schemas import {table_name.capitalize()}Create, {table_name.capitalize()} as {table_name.capitalize()}Schema\n"
            f"from ..database import get_db\n\n"
            f"router = APIRouter(prefix='/{table_name.lower()}', tags=['{table_name.lower()}'])\n\n"
            f"@router.get('/', response_model=list[{table_name.capitalize()}Schema])\n"
            f"def read_{table_name.lower()}s(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):\n"
            f"    return db.query({table_name.capitalize()}Model).offset(skip).limit(limit).all()\n\n"
            f"@router.post('/', response_model={table_name.capitalize()}Schema)\n"
            f"def create_{table_name.lower()}(item: {table_name.capitalize()}Create, db: Session = Depends(get_db)):\n"
            f"    db_item = {table_name.capitalize()}Model(**item.dict())\n"
            f"    db.add(db_item)\n    db.commit()\n    db.refresh(db_item)\n"
            f"    return db_item\n\n"
        )
        endpoint_files[f"{table_name}.py"] = endpoint_code

        # Add router import to __init__.py
        init_code += f"from .{table_name} import router as {table_name}_router\n"

    # Add all routers to `routers` list in `__init__.py`
    init_code += "\nrouters = [\n"
    for table_name in table_names:
        init_code += f"    {table_name}_router,\n"
    init_code += "]\n"

    return models_code, schemas_code, endpoint_files, database_code, init_code, main_code


if __name__ == "__main__":
    csv_file = 'model.csv'
    output_dir = 'output/fastapi'

    models_code, schemas_code, endpoint_files, database_code, init_code, main_code = generate_fastapi_files_with_database(csv_file)

    # Ensure output directories exist
    os.makedirs(os.path.join(output_dir, 'endpoints'), exist_ok=True)

    # Save models.py
    with open(os.path.join(output_dir, 'models.py'), 'w') as f:
        f.write(models_code)

    # Save schemas.py
    with open(os.path.join(output_dir, 'schemas.py'), 'w') as f:
        f.write(schemas_code)

    # Save database.py
    with open(os.path.join(output_dir, 'database.py'), 'w') as f:
        f.write(database_code)

    # Save individual endpoint files
    for filename, content in endpoint_files.items():
        with open(os.path.join(output_dir, 'endpoints', filename), 'w') as f:
            f.write(content)

    # Save __init__.py for endpoints
    with open(os.path.join(output_dir, 'endpoints', '__init__.py'), 'w') as f:
        f.write(init_code)

    # Save main.py
    with open(os.path.join(output_dir, 'main.py'), 'w') as f:
        f.write(main_code)

    # Save requirements.txt
    with open(os.path.join(output_dir, 'requirements.txt'), 'w') as f:
        f.write("fastapi\nsqlalchemy\nuvicorn\nrequests\n")