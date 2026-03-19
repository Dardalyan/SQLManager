from typing import Any, ClassVar, Type, TypeVar

from sqlalchemy.orm import Session

from SQLManager.manager import HintBase, StaticBase, SQLManager

T = TypeVar("T", bound="BaseModel")


class BaseModel:
    """
    Base ORM model class that provides shared CRUD operations for all child models.

    This base class is designed for SQLAlchemy models that inherit from `StaticBase`.
    It allows every child model to use common class-level query and persistence methods
    such as `all`, `first`, `get_by_id`, `filter_by`, `add`, `update`, and `delete`
    without rewriting the same logic repeatedly.

    The generic type variable `T` is used only for type hinting. It allows type checkers
    and IDEs to understand that calling `User.all()` returns `list[User]`, while
    calling `BankTransactions.first()` returns `BankTransactions | None`.

    Notes:
        - A SQLManager instance must be bound first by calling `use(manager)`.
        - Write operations do not commit automatically.
        - Call `commit()` manually when you want to persist changes.
        - Call `rollback()` to cancel pending changes.


    """

    __abstract__ = True
    _db: ClassVar[SQLManager | None] = None
    __session: ClassVar[Session | None] = None

    @classmethod
    def __validate_session(cls):
        if cls.__session is None: raise ValueError(".use() must be called before query execution.")

    @classmethod
    def use(cls, db: SQLManager) -> None:
        """
        Binds the given SQLManager instance to the current model class.

        After binding, all query and persistence methods will use the session
        created by this SQLManager.

        Args:
            db: SQLManager instance to bind to the model.

        Returns:
            None

        """
        cls._db = db
        cls.__session = cls._db.Session
        

    @classmethod
    def all(cls: Type[T]) -> list[T]:
        """
        Returns all records of the current model.

        Returns:
            A list containing all ORM objects mapped to the current model.

        """
        cls.__validate_session()
        session = cls.__session
        return session.query(cls).all()

    @classmethod
    def first(cls: Type[T]) -> T | None:
        """
        Returns the first record of the current model.

        Returns:
            The first ORM object if at least one record exists, otherwise None.

        """
        cls.__validate_session()
        session = cls.__session
        return session.query(cls).first()

    @classmethod
    def get_by_id(cls: Type[T], id_value: Any) -> T | None:
        """
        Returns a single record by its primary key value.

        Args:
            id_value: Primary key value of the target row.

        Returns:
            The matching ORM object if found, otherwise None.

        """
        cls.__validate_session()
        session = cls.__session
        return session.get(cls, id_value)

    @classmethod
    def filter_by(cls: Type[T], **kwargs) -> list[T]:
        """
        Returns all records filtered by the given keyword arguments.

        Args:
            **kwargs: Column-value pairs passed to SQLAlchemy `filter_by`.

        Returns:
            A list of matching ORM objects.

        """
        cls.__validate_session()
        session = cls.__session
        return session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def add(cls: Type[T], obj: T) -> T:
        """
        Adds a single ORM object to the current session.

        This method stages the object for insertion but does not commit.

        Args:
            obj: ORM object instance to add.

        Returns:
            The same object that was added.

        """
        cls.__validate_session()
        session = cls.__session
        session.add(obj)
        return obj

    @classmethod
    def add_range(cls: Type[T], objects: list[T]) -> list[T]:
        """
        Adds multiple ORM objects to the current session.

        This method stages all objects for insertion but does not commit.

        Args:
            objects: List of ORM object instances to add.

        Returns:
            The same list of objects that was added.

        """
        cls.__validate_session()
        session = cls.__session
        session.add_all(objects)
        return objects

    @classmethod
    def update(cls: Type[T], obj: T) -> T:
        """
        Attaches or re-attaches a single ORM object to the current session.

        This is useful when the object has already been modified in memory
        and should be tracked by SQLAlchemy before commit.

        Args:
            obj: Modified ORM object instance.

        Returns:
            The same object that was attached.

        """
        cls.__validate_session()
        session = cls.__session
        session.add(obj)
        return obj

    @classmethod
    def update_range(cls: Type[T], objects: list[T]) -> list[T]:
        """
        Attaches or re-attaches multiple modified ORM objects to the current session.

        This method is useful for bulk update scenarios where objects have already
        been changed in memory.

        Args:
            objects: List of modified ORM object instances.

        Returns:
            The same list of objects that was attached.

        """
        cls.__validate_session()
        session = cls.__session
        session.add_all(objects)
        return objects

    @classmethod
    def delete(cls: Type[T], obj: T) -> T:
        """
        Marks a single ORM object for deletion in the current session.

        This method does not commit automatically.

        Args:
            obj: ORM object instance to delete.

        Returns:
            The same object that was marked for deletion.

        """
        cls.__validate_session()
        session = cls.__session
        session.delete(obj)
        return obj

    @classmethod
    def delete_range(cls: Type[T], objects: list[T]) -> list[T]:
        """
        Marks multiple ORM objects for deletion in the current session.

        This method does not commit automatically.

        Args:
            objects: List of ORM object instances to delete.

        Returns:
            The same list of objects that was marked for deletion.

        """
        cls.__validate_session()
        session = cls.__session
        for obj in objects:
            session.delete(obj)
        return objects

    @classmethod
    def commit(cls) -> None:
        """
        Commits the current session transaction.

        This permanently persists all staged changes to the database.

        Returns:
            None

        """
        session = cls.__session
        session.commit()

    @classmethod
    def rollback(cls) -> None:
        """
        Rolls back the current session transaction.

        This cancels all uncommitted changes currently staged in the session.

        Returns:
            None

        """
        cls.__validate_session()
        session = cls.__session
        session.rollback()

    @classmethod
    def flush(cls) -> None:
        """
        Flushes pending changes to the database without committing.

        This sends staged SQL statements to the database while keeping
        the current transaction open.

        Returns:
            None

        """
        cls.__validate_session()
        session = cls.__session
        session.flush()



class StaticBaseModel(BaseModel,StaticBase):
    __abstract__ = True

class HintBaseModel(BaseModel,HintBase):
    __abstract__ = True