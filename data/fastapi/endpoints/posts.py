from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..models import Posts as PostsModel
from ..schemas import PostsCreate, Posts as PostsSchema
from ..database import get_db

router = APIRouter(prefix='/posts', tags=['posts'])

@router.get('/', response_model=list[PostsSchema])
def read_postss(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(PostsModel).offset(skip).limit(limit).all()

@router.post('/', response_model=PostsSchema)
def create_posts(item: PostsCreate, db: Session = Depends(get_db)):
    db_item = PostsModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

