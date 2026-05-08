from manager import StaticBase, HintBase


class BaseModel:
    """
    Base ORM model marker class.

    This class is used as a shared parent for ORM model base types in SQLManager.
    It does not provide query, persistence, or transaction methods.

    Persistence operations such as querying, adding, updating, deleting,
    committing, rolling back, and flushing are handled by BaseRepository.

    Use:
        - StaticBaseModel for code-first, migration-aware models.
        - HintBaseModel for database-first explicit models.

    Notes:
        - This class is abstract and should not be mapped directly.
        - Domain-specific behavior can still be added to child model classes.
        - Database access should be handled through repository classes.
    """

    __abstract__ = True


class StaticBaseModel(BaseModel, StaticBase):
    """
    Base class for code-first ORM models.

    Use this class when Python model classes are the source of truth for
    database schema generation and Alembic migration tracking.

    Models inheriting from this class are connected to StaticBase metadata,
    which is used by the migration system.

    Example:
        class Product(StaticBaseModel):
            __tablename__ = "products"
    """

    __abstract__ = True


class HintBaseModel(BaseModel, HintBase):
    """
    Base class for database-first explicit ORM models.

    Use this class when the database schema already exists, but you still want
    explicit Python model classes for readability, IDE support, and type hints.

    Models inheriting from this class are not intended to drive migrations.
    They are prepared against the existing database schema through SQLManager.

    Example:
        class User(HintBaseModel):
            __tablename__ = "users"
    """

    __abstract__ = True