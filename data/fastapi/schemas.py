from pydantic import BaseModel

class UserBase(BaseModel):
    id: int
    username: str
    age: int
    joined_at: str
    parent_id: int

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class PostsBase(BaseModel):
    id: int
    user_id: int
    content: str

class PostsCreate(PostsBase):
    pass

class Posts(PostsBase):
    id: int

    class Config:
        orm_mode = True

