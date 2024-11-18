from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..models import Users as UsersModel
from ..schemas import UsersCreate, Users as UsersSchema
from ..database import get_db

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/', response_model=list[UsersSchema])
def read_userss(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(UsersModel).offset(skip).limit(limit).all()

@router.post('/', response_model=UsersSchema)
def create_users(item: UsersCreate, db: Session = Depends(get_db)):
    db_item = UsersModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

