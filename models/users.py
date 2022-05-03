from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
DeclarativeBase = declarative_base()

class Users(DeclarativeBase):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    chat_id = Column('chat_id', Integer)
    firstname = Column('firstname', String)
    lastname = Column('lastname', String)
    type = Column('type', String, default='user')
    center_id = Column('center_id', Integer)
    state = Column('state', String)
    created = Column('created', DateTime)
    updated = Column('updated', DateTime)