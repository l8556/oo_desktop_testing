# -*- coding: utf-8 -*-
import codecs
import json
import string
import zipfile
from os import listdir, makedirs, scandir, remove, walk
from os.path import exists, isfile, isdir, join, getctime, basename, getsize, relpath
from random import randint, choice
from shutil import move, copytree, copyfile, rmtree
from subprocess import Popen, PIPE, getoutput

import psutil
from requests import get, head
from rich import print
from rich.progress import track

from .host_info import HostInfo


class FileUtils:
    @staticmethod
    def read_json(path_to_json: str, encoding: str = "utf_8_sig") -> json:
        with codecs.open(path_to_json, mode="r", encoding=encoding) as file:
            return json.load(file)

    @staticmethod
    def write_json(path_to, data, mode='w'):
        if not exists(path_to):
            return print(f"|WARNING| The path to json file_name does not exist: {path_to}")
        with open(path_to, mode) as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def delete_last_slash(path):
        return path.rstrip(path[-1]) if path[-1] in ['/', '\\'] else path

    @staticmethod
    def make_tmp_file(path: str, tmp_dir: str = './tmp') -> str:
        FileUtils.create_dir(tmp_dir) if not exists(tmp_dir) else ...
        tmp_file_path = FileUtils.random_name(tmp_dir, path.split(".")[-1])
        FileUtils.copy(path, tmp_file_path, stdout=False)
        return tmp_file_path

    @staticmethod
    def get_dir_paths(path: str, end_dir: str = None, dir_include: str = None) -> list:
        dir_paths = []
        for root, dirs, files in walk(path):
            for dir_name in dirs:
                if end_dir:
                    if dir_name.lower().endswith(end_dir if isinstance(end_dir, tuple) else end_dir.lower()):
                        dir_paths.append(join(root, dir_name))
                elif dir_include:
                    if dir_include in dir_name:
                        dir_paths.append(join(root, dir_name))
                else:
                    dir_paths.append(join(root, dir_name))
        return dir_paths

    @staticmethod
    def get_paths(
            path: str,
            extension: "tuple | str" = None,
            names: list = None,
            exceptions_files: list = None,
            exceptions_dirs: list = None,
            dir_include: str = None
    ) -> list:
        ext_dirs = [join(path, ext_path) for ext_path in exceptions_dirs] if exceptions_dirs else ...

        file_paths = []
        for root, dirs, files in walk(path):
            for filename in files:
                if exceptions_files and filename in exceptions_files:
                    continue
                if exceptions_dirs and [path for path in ext_dirs if path in root]:
                    continue
                if dir_include and dir_include not in basename(root):
                    continue
                if names:
                    file_paths.append(join(root, filename)) if filename in names else ...
                elif extension:
                    if filename.lower().endswith(extension if isinstance(extension, tuple) else extension.lower()):
                        file_paths.append(join(root, filename))
                else:
                    file_paths.append(join(root, filename))
        return file_paths

    # path insert with file_name name
    @staticmethod
    def copy(path_from, path_to, stdout=True):
        if not exists(path_from):
            return print(f"[bold red]|COPY WARNING| Path from not exist: {path_from}")
        if isdir(path_from):
            copytree(path_from, path_to)
        elif isfile(path_from):
            copyfile(path_from, path_to)
        if exists(path_to):
            return print(f'[green]|INFO| Copied to: {path_to}') if stdout else ...
        return print(f'[bold red]|COPY WARNING| File not copied: {path_to}')

    @staticmethod
    def last_modified_file(dir_path):
        files = FileUtils.get_paths(dir_path, exceptions_files=['.DS_Store'])
        return max(files, key=getctime) if files else print('[bold red]|WARNING| Last modified file not found')

    @staticmethod
    def move(path_from, path_to):
        if exists(path_from):
            move(path_from, path_to)
            return print("[bold red]|MOVE WARNING| File not moved") if not exists(path_to) else ...
        return print(f"[bold red]|MOVE WARNING| File not exist: {path_from}")

    @staticmethod
    def create_dir(dir_path: "str | tuple", stdout=True) -> None:
        for _dir_path in dir_path if isinstance(dir_path, tuple) else [dir_path]:
            if not exists(_dir_path):
                makedirs(_dir_path, exist_ok=True)
                if isdir(_dir_path):
                    print(f'[green]|INFO| Folder Created: {_dir_path}') if stdout else ...
                    continue
                print(f'[bold red]|WARNING| Create folder warning. Folder not created: {_dir_path}')
                continue
            print(f'[green]|INFO| Folder exists: {_dir_path}') if stdout else ...

    @staticmethod
    def compress_files(path, archive_path=None, delete=False):
        archive = archive_path if archive_path else join(path, f"{basename(path)}.zip")
        if not exists(path):
            return print(f'[bold red]| COMPRESS WARNING| Path for compression does not exist: {path}')
        print(f'[green]|INFO| Compressing: {path}')
        with zipfile.ZipFile(archive, 'w') as zip_archive:
            if isfile(path):
                zip_archive.write(path, basename(path), compress_type=zipfile.ZIP_DEFLATED)
            elif isdir(path):
                for file in track(FileUtils.get_paths(path), description=f"[red]Compressing dir: {basename(path)}"):
                    if basename(file) not in ['.DS_Store', f"{basename(archive)}"]:
                        zip_archive.write(file, relpath(file, path), compress_type=zipfile.ZIP_DEFLATED)
            else:
                return print(f"[red]|WARNING| The path for archiving is neither a file_name nor a directory: {path}")
        if exists(archive) and getsize(archive) != 0:
            FileUtils.delete(path) if delete else ...
            return print(f"[green]|INFO| Success compressed: {archive}")
        print(f"[WARNING] Archive not exists: {archive}")

    @staticmethod
    def unpacking_zip_file(archive_path, execute_path, delete_archive=False):
        with zipfile.ZipFile(archive_path) as zip_archive:
            zip_archive.extractall(execute_path)
        FileUtils.delete(archive_path) if delete_archive else ...

    @staticmethod
    def delete(path: "str | tuple", all_from_folder: bool = False, silence: bool = False) -> None:
        for _path in path if isinstance(path, tuple) else [path]:
            if not exists(_path):
                print(f"[bold red]|DELETE WARNING| Path not exist: {_path}") if not silence else ...
                continue
            if isdir(_path):
                rmtree(_path, ignore_errors=True)
                if all_from_folder:
                    FileUtils.create_dir(_path, stdout=False)
                    if any(scandir(_path)):
                        print(f"[bold red]|DELETE WARNING| Not all files are removed from directory: {_path}")
                        continue
                    print(f'[green]|INFO| Folder is cleared') if not silence else ...
                    continue
            elif isfile(_path):
                remove(_path)
            if exists(_path):
                print(f"[bold red]|DELETE WARNING| Folder is not deleted: {_path}")
                continue
            print(f'[green]|INFO| Deleted: {_path}') if not silence else ...

    @staticmethod
    def random_string(path_to_dir, chars=string.ascii_uppercase + string.digits, num_chars=50, extension=None):
        while True:
            random_string = ''.join(choice(chars).lower() for _ in range(int(num_chars)))
            random_path = join(path_to_dir, f"{random_string}.{extension}" if extension else random_string)
            if not exists(random_path):
                return random_path

    @staticmethod
    def random_name(path, extension=None) -> str:
        while True:
            name = f'{randint(500, 50000)}.{extension.replace(".", "")}' if extension else f'{randint(500, 50000)}'
            random_path = join(path, name)
            if not exists(random_path):
                return random_path

    @staticmethod
    def fix_double_folder(dir_path):
        path = join(dir_path, basename(dir_path))
        if isdir(path):
            for file in listdir(path):
                FileUtils.move(join(path, file), join(dir_path, file))
            if not any(scandir(path)):
                print("[green]|INFO| Fixed double folder")
                return FileUtils.delete(path)
            print("[red]|WARNING| Not all objects are moved")

    @staticmethod
    def get_headers(url):
        status = head(url)
        if status.status_code == 200:
            return status.headers
        print(f"[bold red]|WARNING| Can't get headers\nURL:{url}\nResponse: {status.status_code}")
        return False

    @staticmethod
    def download_file(url: str, dir_path: str, name: str = None) -> None:
        FileUtils.create_dir(dir_path, stdout=False)
        _name = name if name else basename(url)
        file_path = join(dir_path, _name)
        with get(url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as file:
                for chunk in track(r.iter_content(chunk_size=1024 * 1024), description=f'[red] Downloading: {_name}'):
                    if chunk:
                        file.write(chunk)
        print(f"[bold green]|INFO| File Saved to: {file_path}" if isfile(file_path) else f"[red]|WARNING| Not exist")
        if int(getsize(file_path)) != int(r.headers['Content-Length']):
            print(f"[red]|WARNING| Size different\nFile:{getsize(file_path)}\nOn server:{r.headers['Content-Length']}")

    @staticmethod
    def find_in_line_by_key(text: str, key: str, split_by: str = '\n', separator: str = ':') -> "str | None":
        for line in text.split(split_by):
            if separator in line:
                _key, value = line.strip().split(separator, 1)
                if _key.lower() == key.lower():
                    return value.strip()

    @staticmethod
    def change_access(dir_path: str, mode: str = '+x'):
        if HostInfo().os == 'windows':
            return print("[bold red]|WARNING| Can't change access on windows")
        FileUtils.run_command(f'chmod {mode} {join(FileUtils.delete_last_slash(dir_path))}/*')

    @staticmethod
    def file_reader(file_path, mode='r'):
        with open(file_path, mode) as file:
            return file.read()

    @staticmethod
    def file_writer(file_path, text, mode='w'):
        with open(file_path, mode) as file:
            file.write(text)

    @staticmethod
    def output_cmd(command):
        return getoutput(command)

    @staticmethod
    def terminate_process(name_list: list) -> None:
        for process in psutil.process_iter():
            for terminate_process in name_list:
                if terminate_process in process.name():
                    try:
                        process.terminate()
                    except Exception as e:
                        print(f'[bold red]|Warning| Exception when terminate process {terminate_process}: {e}')

    @staticmethod
    def run_command(command):
        popen = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = popen.communicate()
        popen.wait()
        stdout = stdout.strip().decode('utf-8', errors='ignore')
        stderr = stderr.strip().decode('utf-8', errors='ignore')
        popen.stdout.close(), popen.stderr.close()
        return stdout, stderr
