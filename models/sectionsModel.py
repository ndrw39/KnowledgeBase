from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
declarativeBase = declarative_base()

class sectionsModel(declarativeBase):
    __tablename__ = 'Sections'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    center_id = Column('center_id', Integer)
    parent_id = Column('parent_id', Integer)
    created = Column('created', DateTime)
    updated = Column('updated', DateTime)

    def getSections(bd,centerID,parentID = None):
        data = {
            "center_id" : centerID,
            "parent_id" : None
        }

        if parentID:
            data['parent_id'] = parentID

        return bd.query(sectionsModel).filter_by(**data).all()

    def add(bd, name, centerID, parentID):
            data = {
               "name": name,
               "created": datetime.now(),
               "updated": datetime.now(),
               "center_id" : centerID,
            }

            if parentID:
                data['parent_id'] = parentID

            add = sectionsModel(**data)
            bd.add(add)
            bd.commit()