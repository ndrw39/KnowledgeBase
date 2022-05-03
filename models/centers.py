from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
DeclarativeBase = declarative_base()

class Centers(DeclarativeBase):
    __tablename__ = 'Centers'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    created = Column('created', DateTime)
    updated = Column('updated', DateTime)