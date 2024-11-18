from pydantic import BaseModel

class UserBase(BaseModel):
    id: int
    username: str
    age: int
    joined_at: str
    user_id: int

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

