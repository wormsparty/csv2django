from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    age = Column(Integer)
    joined_at = Column(Date)
    user = Column(Integer, ForeignKey('user.id'))

