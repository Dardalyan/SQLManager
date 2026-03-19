import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config

from FileManager import FileManager
from SQLManager.manager import SQLManager


class Migration:

    def __init__(self,manager:SQLManager,model_import:str,auto_migrate:bool=False):
        self.manager = manager
        self.root = self.__find_project_root()
        self.location = self.__find_project_root() / "migrations"
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
        ini_path = str(self.__find_project_root() / "alembic.ini")
        command.init(Config(ini_path), self.path)
        self.__write_env_file()


    @property
    def config(self) -> Config:
        return self.__config

    def __refresh_config(self):
        self.__config.set_main_option("script_location", self.path)
        self.__config.set_main_option("sqlalchemy.url", self.manager.connection_string)


    def make_migration(self,message:str|None,autogenerate:bool=True) -> None:
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
        self.__refresh_config()
        self.repair_if_needed()
        command.upgrade(self.config, migration)


    def downgrade_migration(self, migration:str = '-1'):
        self.__refresh_config()
        self.repair_if_needed()
        command.downgrade(self.config, migration)

    def repair_if_needed(self) -> None:
        command.ensure_version(self.config)

    def reset_migrations(self) -> None:
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
        self.reset_migrations()
        self.make_migration(message=message)
        self.update_database()

    def stamp_head(self) -> None:
        self.__refresh_config()
        command.stamp(self.config, "head")


    def __find_project_root(
            self,
            start_path: str | Path | None = None,
            markers: tuple[str, ...] = ( ".git", "requirements.txt",".venv", ".gitignore")
        ) -> Path:

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
