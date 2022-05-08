from models.users import UsersModel
from datetime import datetime
from common.database import DatabaseConnection


class UsersHelper:

    @staticmethod
    def getUser(chat_id: int) -> UsersModel:
        session = DatabaseConnection()
        return session.query(UsersModel).filter_by(chat_id=chat_id).first()

    @staticmethod
    def createUser(chat_id, firstname, lastname) -> UsersModel:
        session = DatabaseConnection()
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
        return UsersHelper.getUser(chat_id)

    @staticmethod
    def is_admin(chat_id) -> bool:
        session = DatabaseConnection()
        user_data = session.query(UsersModel).filter_by(chat_id=chat_id).first()
        if not user_data:
            return False

        return user_data.type == "admin"

    @staticmethod
    def update_center(user_id, center_id) -> None:
        session = DatabaseConnection()
        session.query(UsersModel).filter_by(chat_id=user_id).update({"center_id": center_id})
        session.commit()

    @staticmethod
    def change_type(user_id, new_type) -> None:
        session = DatabaseConnection()
        session.query(UsersModel).filter_by(chat_id=user_id).update({"type": new_type})
        session.commit()
