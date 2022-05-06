from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime


class SectionsModel(declarative_base()):
    __tablename__ = 'Sections'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    center_id = Column('center_id', Integer)
    parent_id = Column('parent_id', Integer)
    created = Column('created', DateTime)
    updated = Column('updated', DateTime)
