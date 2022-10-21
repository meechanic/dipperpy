#!/usr/bin/env python3
import sys
from dipperpy import *
import json


def parse_args(argv):
    self_name = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(prog=self_name,
                                     description="Extracts structure unints from python code entities")
    parser.add_argument("-p", "--path", type=str, help="Filesystem path")
    parser.add_argument("-m", "--module", type=str, help="Module path")
    return parser.parse_args(sys.argv[1:])


def main():
    args = parse_args(sys.argv)
    dpr = Dipper(args)
    #confs = dpr.get_confs()
    #print_traceback=confs["main"]["print_traceback"]
    obj = {}
    obj['classes'] = list_classes_by_module_path(args.path)
    obj['modules'] = list_modules_by_module_path(args.path)
    obj['data'] = list_data_by_module_path(args.path)
    json.dump(obj, sys.stdout, indent=4, default=str, ensure_ascii=False)


if __name__ == "__main__":
    main()
