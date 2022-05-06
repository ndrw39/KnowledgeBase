from models.users import UsersModel
from datetime import datetime


class UsersHelper:

    @staticmethod
    def getUser(session, chat_id):
        return session.query(UsersModel).filter_by(chat_id=chat_id).first()

    @staticmethod
    def createUser(session, chat_id, firstname, lastname):
        data = {
            "chat_id": chat_id,
            "firstname": firstname,
            "lastname": lastname,
            "type": "user",
            "created": datetime.now(),
            "updated": datetime.now()
        }
        session.add(UsersModel(**data))
        session.commit()
        return UsersHelper.getUser(session, chat_id)

    @staticmethod
    def is_admin(session, chat_id):
        user_data = session.query(UsersModel).filter_by(chat_id=chat_id).first()
        if not user_data:
            return False

        return user_data.type == "admin"
