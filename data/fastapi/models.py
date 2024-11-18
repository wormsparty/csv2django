from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    age = Column(Integer)
    joined_at = Column(Date)
    parent = Column(Integer, ForeignKey('user.id'))

class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    user = Column(Integer, ForeignKey('user.id'))
    content = Column(String, index=True)

