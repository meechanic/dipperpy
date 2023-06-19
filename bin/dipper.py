#!/usr/bin/env python3
import sys
from dipperpy import *
import json
import importlib
import pathlib
from pycg.pycg import CallGraphGenerator
from pycg import formats


def parse_args(argv):
    self_name = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(prog=self_name,
                                     description="Extracts structure unints from python code entities")
    parser.add_argument("-s", "--sys-paths", action="store_true", help="Print sys.path")
    parser.add_argument("-a", "--all", action="store_true", help="All entities (may be applied to different parameters)")
    parser.add_argument("-n", "--names-only", action="store_true",
                        help="Output only names")
    parser.add_argument("-d", "--directory", type=str, help="Directory")
    parser.add_argument("-e", "--depth", type=int, help="Depth")
    parser.add_argument("-p", "--path", type=str, help="Filesystem path to module")
    parser.add_argument("-m", "--module", type=str, help="Module name")
    parser.add_argument("--action", type=str, help="Action")
    parser.add_argument("--mode", type=str, help="Output mode: detailed (default) | classes-functions | short | nodes (fof call-graph) | classes-special (for entities) | functions-special (for entities)")
    parser.add_argument("--max-iter", type=int, default=-1, help="Maximum number of iterations through source code for call graph")
    parser.add_argument("--package", type=str, default=None, help="Package for call graph")
    return parser.parse_args(sys.argv[1:])

def get_nodes_from_callgraph(o):
    nodes_list = []
    for i in o:
        nodes_list.append(i)
        for j in o[i]:
            nodes_list.append(j)
    return nodes_list

def path_to_dotted(p):
    remove_from_end = ".py"
    if p.endswith(remove_from_end):
        p = p[:-len(remove_from_end)]
    p = p.replace("/", ".")
    return p


def main():
    args = parse_args(sys.argv)
    dpr = Dipper(args)
    #confs = dpr.get_confs()
    #print_traceback=confs["main"]["print_traceback"]
    obj = []
    if args.action is None or args.action == "entities":
        if args.directory:
            dir_internals = []
            for e in get_files_list_py(args.directory):
                dir_internals.append({"module_name": e})
            obj = {}
            for h in dir_internals:
                obj[h["module_name"]] = {}
                obj[h["module_name"]]["classes"] = list_classes_by_module_path(args, h["module_name"])
                obj[h["module_name"]]["functions"] = list_functions_by_module_path(args, h["module_name"])
                if not args.mode == "classes-functions":
                    obj[h["module_name"]]["modules"] = list_modules_by_module_path(args, h["module_name"])
                    obj[h["module_name"]]["data"] = list_data_by_module_path(args, h["module_name"])
                    obj[h["module_name"]]["imports"] = list_imports_by_module_path(args, h["module_name"])
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
            obj = {module_path: {}}
            obj[module_path]["classes"] = list_classes_by_module_path(args, module_path)
            obj[module_path]["functions"] = list_functions_by_module_path(args, module_path)
            if not args.mode == "classes-functions":
                obj[module_path]["modules"] = list_modules_by_module_path(args, module_path)
                obj[module_path]["data"] = list_data_by_module_path(args, module_path)
                obj[module_path]["imports"] = list_imports_by_module_path(args, module_path)
        if args.mode == "classes-special":
            ret = []
            for i in obj:
                for j in obj[i]["classes"]:
                    ret.append(path_to_dotted(i) + "." + j["name"])
            obj = ret
        elif args.mode == "functions-special":
            ret = []
            for i in obj:
                for j in obj[i]["functions"]:
                    ret.append(path_to_dotted(i) + "." + j["name"])
            obj = ret
    elif args.action == "call-graph":
        cg = CallGraphGenerator([args.module], args.package, args.max_iter, "call-graph")
        cg.analyze()
        formatter = formats.Simple(cg)
        obj = formatter.generate()
        if args.mode == "nodes":
            obj = get_nodes_from_callgraph(obj)
    json.dump(obj, sys.stdout, indent=4, default=str, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
