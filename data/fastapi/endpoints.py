from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import *
from .database import get_db
from .schemas import *

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/', response_model=list[Users])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Users).offset(skip).limit(limit).all()

@router.post('/', response_model=Users)
def create_users(item: UsersCreate, db: Session = Depends(get_db)):
    db_item = Users(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get('/{item_id}', response_model=Users)
def read_users(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Users).filter(Users.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Users not found')
    return item

@router.delete('/{item_id}')
def delete_users(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Users).filter(Users.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Users not found')
    db.delete(item)
    db.commit()
    return {'message': 'Deleted successfully'}

