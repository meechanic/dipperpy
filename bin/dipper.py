#!/usr/bin/env python3
import sys
from dipperpy import *
import json


def parse_args(argv):
    self_name = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(prog=self_name,
                                     description="Extracts structure unints from python code entities")
    parser.add_argument("-d", "--directory", type=str, help="Directory")
    parser.add_argument("-p", "--path", type=str, help="Filesystem path to module")
    parser.add_argument("-m", "--module", type=str, help="Module name")
    parser.add_argument("--output", type=str, help="Output modules | functions | classes | data")
    return parser.parse_args(sys.argv[1:])


def main():
    args = parse_args(sys.argv)
    dpr = Dipper(args)
    #confs = dpr.get_confs()
    #print_traceback=confs["main"]["print_traceback"]
    obj = []
    if args.output == "classes":
        obj = list_classes_by_module_path(args.path)
    if args.output == "modules":
        obj = list_modules_by_module_path(args.path)
    if args.output == "data":
        obj = list_data_by_module_path(args.path)
    if args.output == "functions":
        obj = list_functions_by_module_path(args.path)
    json.dump(obj, sys.stdout, indent=4, default=str, ensure_ascii=False)


if __name__ == "__main__":
    main()
