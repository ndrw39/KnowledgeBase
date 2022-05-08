import sqlalchemy.ext.declarative as declarative
import config as config
import sqlalchemy
import sqlalchemy.orm as orm


class DatabaseConnection:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            engine = sqlalchemy.create_engine(config.DATABASE_URL)
            declarative_base = declarative.declarative_base()
            declarative_base.metadata.create_all(engine)
            session = sqlalchemy.orm.sessionmaker(bind=engine)
            cls.instance = session()

        return cls.instance
