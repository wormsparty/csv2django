from pydantic import BaseModel

class UsersBase(BaseModel):
    id: int
    username: str
    age: int
    joined_at: str
    user_id: int

class UsersCreate(UsersBase):
    pass

class Users(UsersBase):
    id: int

    class Config:
        orm_mode = True

