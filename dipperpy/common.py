import os
import sys
import argparse
import traceback
import yaml
import pydoc
import inspect
from pathlib import Path
import pkgutil
from io import StringIO
import ast
import pathlib


# common

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def eprint_exception(e, print_traceback=True, need_exit=True):
    eprint(e)
    if print_traceback:
        eprint(traceback.format_exc())
    if need_exit:
        exit(1)


def list_modules_by_module_path(module_path):
    ret = []
    module = pydoc.importfile(module_path)

    # code below inspired by the pydoc source
    modpkgs_names = set()
    if hasattr(module, '__path__'):
        for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
            modpkgs_names.add(modname)
    for key, value in inspect.getmembers(module, inspect.ismodule):
        if value.__name__.startswith(module.__name__ + '.') and key not in modpkgs_names:
            ret.append({"name": value.__name__, "module_path": module_path})

    return ret


def get_files_list(root):
    ret = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            ret.append(pathlib.PurePath(path, name).as_posix())
    return ret


def get_files_list_py(path):
    d_l = get_files_list(path)
    return [e for e in d_l if e.endswith(".py")]

def list_classes_by_module_path(module_path):
    ret = []
    module = pydoc.importfile(module_path)
    for member in inspect.getmembers(module, inspect.isclass):
        if member[1].__module__ == module.__name__:
            ret.append( {"name": member[1].__name__, "qualname": member[1].__qualname__, "module_path": module_path} )
    return ret


def list_functions_by_module_path(module_path):
    ret = []
    module = pydoc.importfile(module_path)
    try:
        all = module.__all__
    except AttributeError:
        all = None
    for member in inspect.getmembers(module, inspect.isroutine):
        if (all is not None or inspect.isbuiltin(member[1]) or inspect.getmodule(member[1]) is module):
            ret.append( {"name": member[0], "module_path": module_path} )
    return ret


def list_imports_by_module_path(module_path):
    ret = []
    with open(module_path, "r") as f:
        content = f.read()
        for node in ast.iter_child_nodes(ast.parse(content)):
            if isinstance(node, ast.ImportFrom):
                for element in node.names:
                    new_obj = {}
                    new_obj["from_what"] = node.module
                    new_obj["what"] = element.name
                    new_obj["as_what"] = ""
                    try:
                        new_obj["as_what"] = element.asname
                    except Exception:
                        pass
                    new_obj["module_path"] = module_path
                    ret.append(new_obj)
            elif isinstance(node, ast.Import):
                for element in node.names:
                    new_obj = {}
                    new_obj["from_what"] = None
                    new_obj["what"] = element.name
                    try:
                        new_obj["as_what"] = element.asname
                    except Exception:
                        pass
                    new_obj["module_path"] = module_path
                    ret.append(new_obj)
    return ret


def list_data_by_module_path(module_path):
    ret = []
    module = pydoc.importfile(module_path)
    reserved_names = ["__builtins__", "__cached__", "__doc__", "__file__", "__loader__", "__name__", "__package__", "__spec__"]
    for member in inspect.getmembers(module, pydoc.isdata):
        if member[0] not in reserved_names:
            ret.append( {"name": member[0], "type_name": type(member[1]).__name__, "module_path": module_path} )
    return ret


class Dipper:

    def __init__(self, args):
        self.args = args
        conf_file = "{}/.config/dipperpy.yaml".format(str(Path.home()))
        self.conf_file_object = {"main": {"print_traceback": True}}
        try:
            with open(conf_file, "r") as f:
                self.conf_file_object = yaml.safe_load(f)
        except Exception as e:
            pass

    def get_confs(self):
        return self.conf_file_object

    def get_args(self):
        return self.args
