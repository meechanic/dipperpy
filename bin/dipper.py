#!/usr/bin/env python3
import sys
from dipperpy import *
import json
import importlib
import pathlib


def parse_args(argv):
    self_name = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(prog=self_name,
                                     description="Extracts structure unints from python code entities")
    parser.add_argument("-s", "--sys-paths", action="store_true", help="Print sys.path")
    parser.add_argument("-a", "--all", action="store_true", help="All entities (may be applied to different parameters)")
    parser.add_argument("-d", "--directory", type=str, help="Directory")
    parser.add_argument("-e", "--depth", type=int, help="Depth")
    parser.add_argument("-p", "--path", type=str, help="Filesystem path to module")
    parser.add_argument("-m", "--module", type=str, help="Module name")
    parser.add_argument("--output", type=str, help="Output modules | functions | classes | data | all")
    return parser.parse_args(sys.argv[1:])


def main():
    args = parse_args(sys.argv)
    dpr = Dipper(args)
    #confs = dpr.get_confs()
    #print_traceback=confs["main"]["print_traceback"]
    obj = []
    if args.directory:
        dir_internals = []
        for e in get_files_list_py(args.directory):
            dir_internals.append({"module_name": e})
        if args.output == "classes":
            for h in dir_internals:
                obj = obj + list_classes_by_module_path(h["module_name"])
        elif args.output == "modules":
            for h in dir_internals:
                obj = obj + list_modules_by_module_path(h["module_name"])
        elif args.output == "data":
            for h in dir_internals:
                obj = obj + list_data_by_module_path(h["module_name"])
        elif args.output == "functions":
            for h in dir_internals:
                obj = obj + list_functions_by_module_path(h["module_name"])
        elif args.output == "imports":
            for h in dir_internals:
                obj = obj + list_imports_by_module_path(h["module_name"])
        elif args.output == "all":
            obj = {}
            for h in dir_internals:
                obj[h["module_name"]] = {}
                obj[h["module_name"]]["classes"] = list_classes_by_module_path(h["module_name"])
                obj[h["module_name"]]["modules"] = list_modules_by_module_path(h["module_name"])
                obj[h["module_name"]]["data"] = list_data_by_module_path(h["module_name"])
                obj[h["module_name"]]["functions"] = list_functions_by_module_path(h["module_name"])
                obj[h["module_name"]]["imports"] = list_imports_by_module_path(h["module_name"])
        else:
            obj = dir_internals
    elif args.sys_paths:
        for p in sys.path:
            if not args.all:
                if p == pathlib.Path().parent.resolve().as_posix():
                    continue
                if p == pathlib.Path(pathlib.Path(__file__).resolve()).parent.as_posix():
                    continue
            obj.append({"sys_path_component": p})
    else:
        module_path = ""
        if args.module:
            module_path = importlib.util.find_spec(args.module).origin
        if args.path:
            module_path = args.path
        if args.output == "classes":
            obj = list_classes_by_module_path(module_path)
        elif args.output == "modules":
            obj = list_modules_by_module_path(module_path)
        elif args.output == "data":
            obj = list_data_by_module_path(module_path)
        elif args.output == "functions":
            obj = list_functions_by_module_path(module_path)
        elif args.output == "imports":
            obj = list_imports_by_module_path(module_path)
        elif args.output == "all":
            obj = {module_path: {}}
            obj[module_path]["classes"] = list_classes_by_module_path(module_path)
            obj[module_path]["modules"] = list_modules_by_module_path(module_path)
            obj[module_path]["data"] = list_data_by_module_path(module_path)
            obj[module_path]["functions"] = list_functions_by_module_path(module_path)
            obj[module_path]["imports"] = list_imports_by_module_path(module_path)
        else:
            pass
    json.dump(obj, sys.stdout, indent=4, default=str, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
