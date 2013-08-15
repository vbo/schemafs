import json
import argparse
import os
import os.path

from . import dump


_pj = os.path.join
DIR_PROJECT = ".schemafs"
DIR_DUMPS_WORKING = _pj(DIR_PROJECT, 'dumps/woking')


def table_path(table):
    return "%s.sql" % table


def function_path(func):
    return "%s.sql" % func


class Ctrl(object):

    def __init__(self):
        pass

    def pull(self, remote):
        pass

    def push(self, remote):
        pass

    def init(self, directory, server, db, use_existing):
        if not use_existing:
            raise NotImplemented()
        os.mkdir(DIR_PROJECT)
        os.makedirs(DIR_DUMPS_WORKING)
        with open(_pj(DIR_PROJECT, 'config'), 'w') as config_file:
            data = {
                'directory': directory,
                'server': server,
                'databases': db,
            }
            config_file.write(json.dumps(data))
            for db_name in db:
                with open(_pj(DIR_DUMPS_WORKING, db_name), 'w') as working:
                    dumped = dump.dump(server, db_name).read()
                    working.write(dumped)
                    struct = dump.parse(dumped)
                    self.struct_to_fs(directory, db_name, struct)

    # todo: this function belongs to some other module
    def struct_to_fs(self, root, db, struct):
        os.makedirs(_pj(root, db))
        # todo: decopypaste
        tables_dir = _pj(root, db, "tables")
        os.mkdir(tables_dir)
        for table, definition in struct["tables"].items():
            with open(_pj(tables_dir, table_path(table)), 'w') as fl:
                fl.write(definition)
        functions_dir = _pj(root, db, "functions")
        os.mkdir(functions_dir)
        for func, definition in struct["functions"].items():
            with open(_pj(functions_dir, function_path(func)), 'w') as fl:
                fl.write(definition)

    def clone(self):
        pass


parser = argparse.ArgumentParser(prog='sfs')
subparsers = parser.add_subparsers()
push_parser = subparsers.add_parser('push')
push_parser.add_argument('remote', nargs='?')
push_parser.set_defaults(cmd='push', remote='origin')
init_parser = subparsers.add_parser('init')
init_parser.add_argument('directory', nargs='?')
init_parser.add_argument('--server', dest='server', nargs='?')
init_parser.add_argument('--db', dest='server', nargs='?')
init_parser.add_argument('--use-existing', dest='use_existing', action='store_true')
init_parser.set_defaults(cmd='init', directory='sql', server='localhost')
pull_parser = subparsers.add_parser('pull')
pull_parser.set_defaults(cmd='pull')
clone_parser = subparsers.add_parser('clone')
clone_parser.set_defaults(cmd='clone')


if __name__ == '__main__':
    args = parser.parse_args()
    cli = Ctrl()
    kwargs = vars(args)
    cmd = kwargs['cmd']
    del kwargs['cmd']
    getattr(cli, cmd)(**kwargs)

