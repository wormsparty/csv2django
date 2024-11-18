from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..models import User as UserModel
from ..schemas import UserCreate, User as UserSchema
from ..database import get_db

router = APIRouter(prefix='/user', tags=['user'])

@router.get('/', response_model=list[UserSchema])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(UserModel).offset(skip).limit(limit).all()

@router.post('/', response_model=UserSchema)
def create_user(item: UserCreate, db: Session = Depends(get_db)):
    db_item = UserModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

