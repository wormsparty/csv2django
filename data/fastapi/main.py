from fastapi import FastAPI
from .endpoints import routers
from .database import create_tables

app = FastAPI()
create_tables()

# Include all routers
for router in routers:
    app.include_router(router)

@app.get('/')
def root():
    return {'message': 'Welcome to the API'}
