from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class UsersModel(declarative_base()):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    chat_id = Column('chat_id', Integer)
    firstname = Column('firstname', String)
    lastname = Column('lastname', String)
    type = Column('type', String, default='user')
    change_type = Column('change_type', Integer, default=0)
    center_id = Column('center_id', Integer)
    created = Column('created', DateTime)
    updated = Column('updated', DateTime)
