import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config

from file_manager import FileManager
from manager import SQLManager


class Migration:
    """
    Alembic-based migration manager for SQLManager.

    This class prepares and manages the Alembic migration environment for a project.
    It initializes the migration folder when needed, updates Alembic configuration,
    rewrites env.py to use SQLManager's StaticBase metadata, and provides helper
    methods for creating, applying, downgrading, resetting, rebuilding, and stamping
    migrations.
    """

    def __init__(self,manager:SQLManager,model_import:str,auto_migrate:bool=False,root:str|None=None):
        """
        Initializes the migration manager.

        Args:
            manager: SQLManager instance that provides the database connection string.
            model_import: Import path of the module or package that contains ORM models.
            auto_migrate: Optional flag stored for external auto-migration workflows.
            root: Optional custom project root path. If None, the project root is detected automatically.

        Raises:
            FileExistsError: If the migrations directory exists but env.py is missing.
        """
        self.manager = manager
        self.root = self.__find_project_root() if root is None else root
        self.location = self.root / "migrations"
        self.path = str(self.location)
        self.__config = Config()
        self.__model_import = model_import
        self.auto_migrate = auto_migrate
        self.fm = FileManager()

        env_path = self.location / "env.py"

        if not self.location.exists():
            self.__initialize()
        elif env_path.exists():
            self.__write_env_file()
        else:
            raise FileExistsError(
                f"Migration directory already exists but env.py is missing: {self.location}. "
                f"Delete the directory and retry, or repair it manually."
            )

    def __initialize(self):
        """
        Initializes a new Alembic migration environment.

        Creates the migrations directory using Alembic and then rewrites env.py
        with the required SQLManager metadata configuration.
        """
        ini_path = str(self.__find_project_root() / "alembic.ini")
        command.init(Config(ini_path), self.path)
        self.__write_env_file()


    @property
    def config(self) -> Config:
        """
        Returns the internal Alembic Config instance.

        Returns:
            Alembic Config object used by migration commands.
        """
        return self.__config

    def __refresh_config(self):
        """
        Refreshes Alembic configuration values.

        Updates the migration script location and database connection URL before
        running Alembic commands.
        """
        self.__config.set_main_option("script_location", self.path)
        self.__config.set_main_option("sqlalchemy.url", self.manager.connection_string)


    def make_migration(self,message:str|None,autogenerate:bool=True) -> None:
        """
        Creates a new Alembic migration revision.

        Args:
            message: Migration message. If empty and autogenerate is False,
                a UUID value is used as the message.
            autogenerate: Whether Alembic should auto-detect schema changes.

        Returns:
            None
        """
        self.__refresh_config()
        self.repair_if_needed()
        if (message is None or message.strip() == "") and not autogenerate: message = str(uuid.uuid4())
        if autogenerate:
            message = "auto_migrate"
            temp =  self.location / 'versions'
            fm = FileManager()
            if temp.exists() and temp.is_dir():
                for filename in [d.name for d in temp.iterdir()]:
                    if message in filename: fm.delete_file(str(temp / filename))
        command.revision(self.config,autogenerate=autogenerate,message=message)

    def update_database(self, migration:str = 'head'):
        """
        Applies migrations to the database.

        Args:
            migration: Target migration revision. Defaults to 'head'.

        Returns:
            None
        """
        self.__refresh_config()
        self.repair_if_needed()
        command.upgrade(self.config, migration)


    def downgrade_migration(self, migration:str = '-1'):
        """
        Downgrades the database to a previous migration revision.

        Args:
            migration: Target downgrade revision. Defaults to '-1'.

        Returns:
            None
        """
        self.__refresh_config()
        self.repair_if_needed()
        command.downgrade(self.config, migration)

    def repair_if_needed(self) -> None:
        """
        Ensures Alembic's version tracking table exists.

        Returns:
            None
        """
        command.ensure_version(self.config)

    def reset_migrations(self) -> None:
        """
        Resets local migration history.

        Deletes migration cache and version files, recreates the versions folder,
        and drops the alembic_version table from the database when it exists.

        Returns:
            None
        """
        if self.location.exists():
            pycache = self.location / "__pycache__"
            if pycache.exists():
                self.fm.delete_folder(str(pycache))


        versions_path = self.location / "versions"

        if versions_path.exists():
            self.fm.delete_folder(str(versions_path))
        self.fm.create_folder(str(versions_path))

        self.manager.set_query("""
        IF OBJECT_ID('alembic_version', 'U') IS NOT NULL
            DROP TABLE alembic_version
        """)
        self.manager.execute()

    def rebuild_migrations(self,message = "initial"):
        """
        Rebuilds migration history from scratch.

        Args:
            message: Message for the newly generated initial migration.

        Returns:
            None
        """
        self.reset_migrations()
        self.make_migration(message=message)
        self.update_database()

    def stamp_head(self) -> None:
        """
        Marks the current database state as the latest migration revision.

        Returns:
            None
        """
        self.__refresh_config()
        command.stamp(self.config, "head")


    def __find_project_root(
            self,
            start_path: str | Path | None = None,
            markers: tuple[str, ...] = ( ".git", "requirements.txt",".venv", ".gitignore")
        ) -> Path:
        """
        Finds the project root by walking upward from a start path.

        Args:
            start_path: Optional path to start searching from.
            markers: File or folder names used to identify the project root.

        Returns:
            Path to the detected project root.

        Raises:
            FileNotFoundError: If none of the marker files or folders are found.
        """

        current = Path(start_path or __file__).resolve()

        if current.is_file():
            current = current.parent

        for directory in (current, *current.parents):
            for marker in markers:
                if (directory / marker).exists():
                    return directory

        raise FileNotFoundError(
            f"Project root not found. None of these markers were found: {markers}"
        )

    def __write_env_file(self):
        """
        Rewrites Alembic env.py for SQLManager migration support.

        Injects StaticBase import, model import, StaticBase.metadata as target metadata,
        and include_object filtering into Alembic's env.py file.

        Raises:
            FileNotFoundError: If env.py does not exist.
            ValueError: If required imports, markers, or metadata lines cannot be found.
        """
        env_path = self.location / "env.py"

        if not env_path.exists():
            raise FileNotFoundError(f"env.py not found at: {env_path}")

        content = env_path.read_text(encoding="utf-8")

        if not self.__model_import:
            raise ValueError("Model import path is empty. Set model import before migration initialization.")

        import re

        static_import = "from SQLManager.manager import StaticBase"
        model_import = f"import {self.__model_import}"

        # StaticBase and model import
        if static_import not in content or model_import not in content:
            marker = "from alembic import context"
            if marker not in content:
                raise ValueError(f"Expected marker not found in env.py: {marker}")

            inject_lines = [marker]

            if static_import not in content:
                inject_lines.append(static_import)

            if model_import not in content:
                inject_lines.append(model_import)

            content = content.replace(
                marker,
                "\n".join(inject_lines),
                1
            )
        else:
            if "import models" in content and self.__model_import != "models":
                content = content.replace("import models", model_import, 1)

        # target_metadata
        if "target_metadata = None" in content:
            content = content.replace(
                "target_metadata = None",
                "target_metadata = StaticBase.metadata",
                1
            )
        elif "target_metadata =" in content:
            content = re.sub(
                r"target_metadata\s*=\s*.*",
                "target_metadata = StaticBase.metadata",
                content,
                count=1
            )
        else:
            insert_after = model_import
            if insert_after not in content:
                raise ValueError(f"Expected model import not found in env.py: {insert_after}")

            content = content.replace(
                insert_after,
                f"{insert_after}\n\ntarget_metadata = StaticBase.metadata",
                1
            )
        include_object_block = """
    def include_object(object, name, type_, reflected, compare_to):
        if type_ == "table":
            return name in target_metadata.tables
        return True
    """.strip()

        if "def include_object(" not in content:
            target_line = "target_metadata = StaticBase.metadata"
            if target_line not in content:
                raise ValueError(f"Expected target_metadata line not found in env.py: {target_line}")

            content = content.replace(
                target_line,
                f"{target_line}\n\n\n{include_object_block}",
                1
            )

        # add include_object for each context.configure(...) call
        if "include_object=include_object" not in content:
            content = re.sub(
                r"context\.configure\((.*?)\)",
                lambda m: self.__inject_include_object_arg(m.group(0)),
                content,
                flags=re.DOTALL
            )

        env_path.write_text(content, encoding="utf-8")

    @staticmethod
    def __inject_include_object_arg(configure_block: str) -> str:
        """
        Injects include_object into a context.configure(...) block.

        Args:
            configure_block: Existing context.configure(...) call as text.

        Returns:
            Updated context.configure(...) block text.
        """
        if "include_object=include_object" in configure_block:
            return configure_block

        insert_pos = configure_block.rfind(")")
        if insert_pos == -1:
            return configure_block

        inner = configure_block[len("context.configure("):insert_pos]

        if inner.strip():
            if inner.rstrip().endswith(","):
                new_inner = inner + "\n    include_object=include_object"
            else:
                new_inner = inner + ",\n    include_object=include_object"
        else:
            new_inner = "\n    include_object=include_object\n"

        return f"context.configure({new_inner})"