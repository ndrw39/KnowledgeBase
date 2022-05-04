from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
declarativeBase = declarative_base()

class usersModel(declarativeBase):
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

    def getOrCreateByTg(bd, tData):
        userData = bd.query(usersModel).filter_by(chat_id=tData.chat.id).all()
        if userData:
            return userData[0]

        data = {
           "chat_id": tData.chat.id,
           "firstname": tData.chat.first_name,
           "lastname": tData.chat.last_name,
           "type": "user",
           "state": "start",
           "created": datetime.now(),
           "updated": datetime.now()
        }
        add = usersModel(**data)
        bd.add(add)
        bd.commit()
        return data