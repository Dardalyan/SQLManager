from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from service import ORMRegistrator
from .BaseManager import SQLBaseManager, SQLEngine

StaticBase = declarative_base()
HintBase = declarative_base(cls=DeferredReflection)


class Meta:
    def __getitem__(self, item):
        return getattr(self, item)

class SQLManager(SQLBaseManager):

    def __init__(self):
        super().__init__()
        self.__session_factory = None
        self.__automap_base = None
        self.__meta = None
        self.__orm:ORMRegistrator|None = None
        self.__model_import = ""


    def setup(self, sql_engine:SQLEngine, ip:str = '127.0.0.1', port: int | None = None, db_name:str= '', user_name:str= '', password:str= '', use_driver: str | None=None):
        super().setup( sql_engine, ip , port , db_name, user_name, password, use_driver)


    def set_orm(self,orm:ORMRegistrator):
        self.__orm = orm


    def connect(self):
        if not self.__model_import:
            raise ValueError("Model import path must be set before connect().")

        super().connect()

        # meta object
        self.__meta = Meta()

        # Static Map
        if self.__orm is not None and any(issubclass(cls, HintBase) for cls in self.__orm.load()):
            HintBase.prepare(self.engine)
            for cls in self.__orm.load():
                setattr(self.__meta, cls.__name__, cls)

        # Automap - Run Time Class Registration
        auto_base = automap_base()
        auto_base.prepare(autoload_with=self.engine)
        self.__automap_base = auto_base
        self.__session_factory = sessionmaker(bind=self.engine)

        for class_name in self.__automap_base.classes.keys():
            if not hasattr(self.__meta, class_name):
                setattr(self.__meta, class_name, getattr(self.__automap_base.classes, class_name))




    @property
    def Meta(self):
        """
        Returns Meta class to access registered Static Models and AutoMapped Dynamic ORM models.
        :return:
        """
        return self.__meta

    @property
    def Session(self) -> Session:
        """
        SQLAlchemy session
        :return: Session
        """
        if self.__session_factory is None:
            raise ValueError(".connect() must be called before session creation")
        return self.__session_factory()

    def set_model_import(self, import_path:str) -> None:
        self.__model_import = import_path

    
    def disconnect(self):
        self.__session_factory = None
        self.__automap_base = None
        self.__meta = None

        super().disconnect()







