from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
declarativeBase = declarative_base()

class centersModel(declarativeBase):
    __tablename__ = 'Centers'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    created = Column('created', DateTime)
    updated = Column('updated', DateTime)

    def getAll(bd):
        return bd.query(centersModel).all()

    def add(bd, centerName):
        data = {
           "name": centerName,
           "created": datetime.now(),
           "updated": datetime.now()
        }
        add = centersModel(**data)
        bd.add(add)
        bd.commit()

    def update(bd, updateId, centerName):
        data = {
           "name": centerName,
           "updated": datetime.now()
        }

        bd.query(centersModel).filter_by(id=updateId).update(data)
        bd.commit()

    def delete(bd, deleteId):
        bd.query(centersModel).filter_by(id=deleteId).delete()