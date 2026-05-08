from typing import Type, Any, TypeVar, Generic

from manager import SQLManager
from model import BaseModel

T = TypeVar("T", bound="BaseModel")


class BaseRepository(Generic[T]):


    
    def __init__(self, db: SQLManager, model:Type[T]) -> None:
        """
        Binds the given SQLManager instance to the current model class.

        After binding, all query and persistence methods will use the session
        created by this SQLManager.

        Args:
            db: SQLManager instance to bind to the model.

        Returns:
            None

        """
        self._db = db
        self.__session = self._db.Session
        self.model = model


    def __validate_session(self):
        if self.__session is None: raise ValueError("Database session is not initialized.")

    
    def all(self) -> list[T]:
        """
        Returns all records of the current model.

        Returns:
            A list containing all ORM objects mapped to the current model.

        """
        self.__validate_session()
        session = self.__session
        return session.query(self.model).all()

    
    def first(self) -> T | None:
        """
        Returns the first record of the current model.

        Returns:
            The first ORM object if at least one record exists, otherwise None.

        """
        self.__validate_session()
        session = self.__session
        return session.query(self.model).first()

    
    def get_by_id(self, id_value: Any) -> T | None:
        """
        Returns a single record by its primary key value.

        Args:
            id_value: Primary key value of the target row.

        Returns:
            The matching ORM object if found, otherwise None.

        """
        self.__validate_session()
        session = self.__session
        return session.get(self, id_value)

    
    def filter_by(self, **kwargs) -> list[T]:
        """
        Returns all records filtered by the given keyword arguments.

        Args:
            **kwargs: Column-value pairs passed to SQLAlchemy `filter_by`.

        Returns:
            A list of matching ORM objects.

        """
        self.__validate_session()
        session = self.__session
        return session.query(self.model).filter_by(**kwargs).all()

    
    def add(self, obj: T) -> T:
        """
        Adds a single ORM object to the current session.

        This method stages the object for insertion but does not commit.

        Args:
            obj: ORM object instance to add.

        Returns:
            The same object that was added.

        """
        self.__validate_session()
        session = self.__session
        session.add(obj)
        return obj

    
    def add_range(self, objects: list[T]) -> list[T]:
        """
        Adds multiple ORM objects to the current session.

        This method stages all objects for insertion but does not commit.

        Args:
            objects: List of ORM object instances to add.

        Returns:
            The same list of objects that was added.

        """
        self.__validate_session()
        session = self.__session
        session.add_all(objects)
        return objects

    
    def update(self, obj: T) -> T:
        """
        Attaches or re-attaches a single ORM object to the current session.

        This is useful when the object has already been modified in memory
        and should be tracked by SQLAlchemy before commit.

        Args:
            obj: Modified ORM object instance.

        Returns:
            The same object that was attached.

        """
        self.__validate_session()
        session = self.__session
        session.add(obj)
        return obj

    
    def update_range(self, objects: list[T]) -> list[T]:
        """
        Attaches or re-attaches multiple modified ORM objects to the current session.

        This method is useful for bulk update scenarios where objects have already
        been changed in memory.

        Args:
            objects: List of modified ORM object instances.

        Returns:
            The same list of objects that was attached.

        """
        self.__validate_session()
        session = self.__session
        session.add_all(objects)
        return objects

    
    def delete(self, obj: T) -> T:
        """
        Marks a single ORM object for deletion in the current session.

        This method does not commit automatically.

        Args:
            obj: ORM object instance to delete.

        Returns:
            The same object that was marked for deletion.

        """
        self.__validate_session()
        session = self.__session
        session.delete(obj)
        return obj

    
    def delete_range(self, objects: list[T]) -> list[T]:
        """
        Marks multiple ORM objects for deletion in the current session.

        This method does not commit automatically.

        Args:
            objects: List of ORM object instances to delete.

        Returns:
            The same list of objects that was marked for deletion.

        """
        self.__validate_session()
        session = self.__session
        for obj in objects:
            session.delete(obj)
        return objects

    
    def commit(self) -> None:
        """
        Commits the current session transaction.

        This permanently persists all staged changes to the database.

        Returns:
            None

        """
        self.__validate_session()
        session = self.__session
        session.commit()

    
    def rollback(self) -> None:
        """
        Rolls back the current session transaction.

        This cancels all uncommitted changes currently staged in the session.

        Returns:
            None

        """
        self.__validate_session()
        session = self.__session
        session.rollback()

    
    def flush(self) -> None:
        """
        Flushes pending changes to the database without committing.

        This sends staged SQL statements to the database while keeping
        the current transaction open.

        Returns:
            None

        """
        self.__validate_session()
        session = self.__session
        session.flush()

