from models.users import UsersModel
from datetime import datetime
from common.database import DatabaseConnection


class UsersHelper:

    @staticmethod
    def getUser(chat_id: int) -> UsersModel:
        session = DatabaseConnection()
        return session.query(UsersModel).filter_by(chat_id=chat_id).first()

    @staticmethod
    def createUser(chat_id: int, firstname: str, lastname: str) -> UsersModel:
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
    def is_admin(chat_id: int) -> bool:
        session = DatabaseConnection()
        user_data = session.query(UsersModel).filter_by(chat_id=chat_id).first()
        if not user_data:
            return False

        return user_data.type == "admin"

    @staticmethod
    def update_center(user_id: int, center_id: int) -> None:
        session = DatabaseConnection()
        session.query(UsersModel).filter_by(chat_id=user_id).update({"center_id": center_id})
        session.commit()

    @staticmethod
    def change_type(user_id: int, new_type: str) -> None:
        session = DatabaseConnection()
        session.query(UsersModel).filter_by(chat_id=user_id).update({"type": new_type})
        session.commit()

    @staticmethod
    def get_admins():
        session = DatabaseConnection()
        admins = session.query(UsersModel).filter_by(type="admin").all()
        return admins
