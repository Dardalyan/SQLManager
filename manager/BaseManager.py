import re
from enum import Enum
from sqlalchemy import create_engine, text, Engine, TextClause


class SQLEngine(Enum):

    NONE = None
    POSTGRES = "postgresql"
    MSSQL = "mssql"
    MYSQL = "mysql"
    MARIADB = "mariadb"



class SQLBaseManager:

    def __init__(self):
        """
        SQL Manager for SQL Alchemy.
        """
        self.connection_string = ""
        self.sql_engine:SQLEngine = SQLEngine.NONE
        self.ip:str = "127.0.0.1"
        self.port:int|None = None
        self.username:str|None = None
        self.password:str|None = None
        self.db_name:str|None = None
        self.driver:str|None = None
        self.engine:Engine|None= None
        self.query:TextClause|None = None
        self.params:dict|None = None

    def setup(self, sql_engine:SQLEngine, ip:str = '127.0.0.1', port: int | None = None, db_name:str= '', user_name:str= '', password:str= '', use_driver: str | None=None):
        """
        Initialize SQL connection string.
        :param sql_engine: Sql Engine.
        :param ip: IP Address.
        :param port: Port Info.
        :param db_name: configuration Name.
        :param user_name: User Credential
        :param password: Password Credential
        :param use_driver: Driver Name.
        :return:
        """
        self.sql_engine = sql_engine
        self.ip = ip
        self.port = port
        self.username = user_name
        self.password = password
        self.db_name = db_name
        self.driver = use_driver

        __conn_str = f"{sql_engine.value}://"  if use_driver is None else f"{sql_engine.value}+{use_driver}://"
        if sql_engine is not SQLEngine.MSSQL:
            __conn_str += f"{user_name}:{password}@" if user_name and password is not None else ""
            __conn_str += f"{ip}" if port is None else f"{ip}:{port}"
            __conn_str += f"/{db_name}"
        else:
            __conn_str += f"{user_name}:{password}@" if user_name and password is not None else ""
            __conn_str += f"{ip}" if port is None else f"{ip}:{port}"
            __conn_str += f"/{db_name}"
            __conn_str += "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes"

        self.connection_string = __conn_str

    def connect(self):
        """
        Connect to SQL engine.
        :return:
        """
        if  self.connection_string == "": raise Exception("Connection string is empty or None")
        self.engine = create_engine(self.connection_string)

    def get_connection(self):
        if self.engine is None:
            raise Exception("Engine is not initialized. Call connect() first.")
        return self.engine.connect()

    def disconnect(self):
        """
        Disconnect from SQL engine.
        """
        if self.engine is not None:
            self.engine.dispose()
            self.engine = None

    def set_query(self, query: str, *args):
        """
        Prepare a raw SQL query for execution and optionally bind positional parameters.

        This method supports `%s` style placeholders in the given SQL query and
        automatically converts them into SQLAlchemy-compatible named parameters
        such as `:param1`, `:param2`, `:param3`, etc.

        Each value passed through `*args` is matched to the corresponding `%s`
        placeholder in order.

        Example:
            Input query:
                "SELECT * FROM users WHERE id = %s AND status = %s"

            Input args:
                (15, "active")

            Generated query:
                "SELECT * FROM users WHERE id = :param1 AND status = :param2"

            Generated params:
                {
                    "param1": 15,
                    "param2": "active"
                }

        Args:
            query (str):
                Raw SQL query string. It may contain zero or more `%s` placeholders.

            *args:
                Positional parameter values to bind into the query. Each argument
                corresponds to one `%s` placeholder in the same order.

        Raises:
            ValueError:
                Raised when the number of `%s` placeholders in the query does not
                match the number of provided arguments.

        Returns:
            None:
                The prepared SQLAlchemy text query is stored in `self.query`,
                and the generated parameter dictionary is stored in `self.params`.
        """
        placeholder_count = len(re.findall(r"%s", query))

        if placeholder_count != len(args):
            raise ValueError(
                f"Placeholder count does not match argument count. "
                f"Expected {placeholder_count} parameter(s), got {len(args)}."
            )

        params = {}

        for index, value in enumerate(args, start=1):
            param_name = f"param{index}"
            query = query.replace("%s", f":{param_name}", 1)
            params[param_name] = value

        self.query = text(query)
        self.params = params

    def execute(self):
        """
        Execute the last prepared query and return the result.

        If the query contains bound parameters prepared by `set_query(...)`,
        they are automatically passed to the SQLAlchemy execution context.
        Otherwise, the query is executed without parameters.

        Raises:
            Exception:
                Raised when the database engine is not initialized.

            ValueError:
                Raised when no query has been prepared before execution.

        Returns:
            CursorResult:
                The SQLAlchemy execution result object returned by `conn.execute(...)`.
        """
        if self.engine is None:
            raise Exception("Engine is not initialized. Call connect() first.")

        if self.query is None:
            raise ValueError("Query is not set. Call set_query() first.")

        try:
            with self.engine.begin() as conn:
                if hasattr(self, "params") and self.params:
                    return conn.execute(self.query, self.params)

                return conn.execute(self.query)

        except Exception as e:
            print(e)
            raise

