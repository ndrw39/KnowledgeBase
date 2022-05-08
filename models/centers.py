from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class CentersModel(declarative_base()):
    __tablename__ = 'Centers'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    sort = Column('sort', Integer, default=0)
    created = Column('created', DateTime)
    updated = Column('updated', DateTime)
