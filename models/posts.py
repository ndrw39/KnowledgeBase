from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime


class PostsModel(declarative_base()):
    __tablename__ = 'Posts'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    text = Column('text', String)
    section_id = Column('section_id', Integer)
    sort = Column('sort', Integer, default=0)
    created = Column('created', DateTime)
    updated = Column('updated', DateTime)
