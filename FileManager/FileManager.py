from enum import Enum
from pathlib import Path
import shutil


class FileOperation(Enum):
    CREATE = 'x'
    READ = 'r'
    WRITE = 'a'
    OVERWRITE = 'w'


class FileManager:

    def __init__(self):
        pass

    def is_file_exist(self,path:str) -> bool:
        return Path(path).exists()

    def is_folder_exist(self,path:str) -> bool:
        folder = Path(path)
        return folder.exists() and folder.is_dir()

    def create_file(self,path:str) -> bool:
        try:
            with open(path, FileOperation.CREATE.value) as file:
                pass
            return True
        except FileExistsError as e:
            print(e)
            return False

    def create_folder(self,path:str) -> bool:
        try:
           if '/' in path:
               Path(path).mkdir(parents=True, exist_ok=True)
           else: Path(path).mkdir(exist_ok=True)

           return True
        except FileExistsError as e:
            print(e)
            return False


    def read_file(self,path:str) ->str:
        try:
            file_content:str = ""
            with open(path, FileOperation.READ.value) as file:
                file_content = file.read()
            return file_content
        except Exception as e:
            print(e)
            return ""


    def write_file(self,path:str,content:str, re_create_content:bool = False) -> bool:
        try:
            if not self.is_file_exist(path): return False
            op = FileOperation.WRITE.value if re_create_content else FileOperation.OVERWRITE.value
            with open(path, op) as file:
                file.write(content)
            return True

        except Exception as e:
            print(e)
            return False

    def copy_file(self,source:str,destination:str) -> bool:
        try:
            if not self.is_file_exist(source): return False
            shutil.copy(source, destination)
            return True
        except Exception as e:
            print(e)
            return False

    def copy_folder(self,source:str,destination:str) -> bool:
        try:
            if not self.is_folder_exist(source): return False
            shutil.copytree(source, destination)
            return True
        except Exception as e:
            print(e)
            return False

    def move_file(self,source:str,destination:str) -> bool:
        try:
            if not self.is_file_exist(source): return False
            shutil.move(source, destination)
            return True
        except Exception as e:
            print(e)
            return False

    def move_folder(self,source:str,destination:str) -> bool:
        try:
            if not self.is_folder_exist(source): return False
            shutil.move(source, destination)
            return True
        except Exception as e:
            print(e)
            return False

    def delete_file(self,path:str) -> bool:
        try:
            if not self.is_file_exist(path): return False
            Path(path).unlink()
            return True

        except Exception as e:
            print(e)
            return False

    def delete_folder(self,path:str) -> bool:
        try:
            if not self.is_file_exist(path): return False
            shutil.rmtree(path)
            return True

        except Exception as e:
            print(e)
            return False






