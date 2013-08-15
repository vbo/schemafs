import json
import shutil
import argparse
import os
import os.path

from . import dump


_pj = os.path.join
DIR_PROJECT = ".schemafs"
DIR_DUMPS_WORKING = _pj(DIR_PROJECT, 'dumps/working')
DIR_CACHE_WORKING_FS = _pj(DIR_PROJECT, 'cache/working/fs')
DIR_CACHE_WORKING_SCHEMA = _pj(DIR_PROJECT, 'cache/working/schema')
CACHE_FS_LAYOUT = False


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

    def diff(self, path):
        pass

    def init(self, directory, server, user, db, use_existing):
        if not use_existing:
            raise NotImplementedError("Init without existing server is not supported yet")
        os.mkdir(DIR_PROJECT)
        os.makedirs(DIR_DUMPS_WORKING)
        os.makedirs(DIR_CACHE_WORKING_FS)
        os.makedirs(DIR_CACHE_WORKING_SCHEMA)
        with open(_pj(DIR_PROJECT, 'config.json'), 'w') as config_file:
            data = {
                'directory': directory,
                'server': server,
                'user': user,
                'databases': db,
            }
            config_file.write(json.dumps(data, indent=4, separators=(',', ': ')) + "\n")
        for db_name in db:
            dumped = dump.dump(server, user, db_name).read()
            with open(_pj(DIR_DUMPS_WORKING, '%s.sql' % db_name), 'w') as working:
                working.write(dumped)
            struct = dump.parse(dumped)
            with open(_pj(DIR_CACHE_WORKING_SCHEMA, "%s.json" % db_name), 'w') as cache:
                cache.write(json.dumps(struct))
            self.struct_to_fs(directory, db_name, struct)


    # todo: this function belongs to some other module
    def struct_to_fs(self, root, db, struct):
        db_root = _pj(root, db)
        os.makedirs(db_root)
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
        if CACHE_FS_LAYOUT:
            shutil.copytree(db_root, _pj(DIR_CACHE_WORKING_FS, db))

    def clone(self):
        pass


# todo: declarative argparse
parser = argparse.ArgumentParser(prog='sfs')
subparsers = parser.add_subparsers()
push_parser = subparsers.add_parser('push')
push_parser.add_argument('remote', nargs='?')
push_parser.set_defaults(cmd='push', remote='origin')
init_parser = subparsers.add_parser('init')
init_parser.add_argument('--dir', dest='directory', nargs='?')
init_parser.add_argument('--server', dest='server', nargs='?')
init_parser.add_argument('--user', dest='user', nargs='?')
init_parser.add_argument('--db', dest='db', nargs='*')
init_parser.add_argument('--use-existing', dest='use_existing', action='store_true')
init_parser.set_defaults(cmd='init', directory='sql', server='localhost', user='postgres', db=None, use_existing=False)
pull_parser = subparsers.add_parser('pull')
pull_parser.set_defaults(cmd='pull')
clone_parser = subparsers.add_parser('clone')
clone_parser.set_defaults(cmd='clone')
diff_parser = subparsers.add_parser('diff')
diff_parser.add_argument('path', nargs='*')
diff_parser.set_defaults(cmd='diff', path=None)


if __name__ == '__main__':
    args = parser.parse_args()
    cli = Ctrl()
    kwargs = vars(args)
    cmd = kwargs['cmd']
    del kwargs['cmd']
    getattr(cli, cmd)(**kwargs)

