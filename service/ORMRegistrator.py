class ORMRegistrator:
    """
    Registry for explicit ORM model classes.

    ORMRegistrator stores model class references and allows SQLManager
    to receive application-defined ORM models without importing them directly.

    This is mainly useful for database-first explicit models based on HintBase
    or HintBaseModel.

    Example:
        registry = ORMRegistrator()
        registry.register(User)
        registry.register(Product)

        db.set_orm(registry)
    """

    def __init__(self):
        """
        Creates an empty ORM model registry.

        Registered models are stored by class name.
        """

        self.__models = {}

    def register(self, cls: type) -> None:
        """
        Registers an ORM model class.

        Args:
            cls: ORM model class to register.

        Returns:
            None
        """

        self.__models[cls.__name__] = cls

    def get_model(self, cls: type | str) -> type:
        """
        Returns a registered ORM model class.

        Args:
            cls: Either the model class itself or the class name as a string.

        Returns:
            The registered ORM model class.

        Raises:
            KeyError: If the given model class or name is not registered.
        """

        if isinstance(cls, type):
            return self.__models[cls.__name__]

        return self.__models[cls]

    def load(self) -> list[type]:
        """
        Returns all registered ORM model classes.

        Returns:
            A list of registered ORM model classes.
        """

        return list(self.__models.values())