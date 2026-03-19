class ORMRegistrator:

    def __init__(self):
        self.__models = {}

    def register(self, cls:type) -> None:
        """
        Registers a type of class.
        :param cls: Class Type to be registered.
        :return: None
        """
        self.__models[cls.__name__] = cls


    def get_model(self,cls:type|str) -> type:
        """
        Returns registered class types
        :param cls: String or Type of registered class.
        :return: The registered class type.
        """
        if isinstance(cls, type):
            return self.__models[cls.__name__]
        else: return self.__models[cls]

    def load(self) -> list[type]:
        """
        Returns all registered class types.
        :return: List of registered class types.
        """
        return list(self.__models.values())
