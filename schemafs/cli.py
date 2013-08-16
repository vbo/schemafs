import json
import shutil
import argparse
import os
from glob import iglob

from . import schema


_pj = os.path.join
DIR_PROJECT = ".schemafs"
DIR_DUMPS_WORKING = _pj(DIR_PROJECT, 'dumps/working')
DIR_CACHE_WORKING_FS = _pj(DIR_PROJECT, 'cache/working/fs')
DIR_CACHE_WORKING_SCHEMA = _pj(DIR_PROJECT, 'cache/working/schema')
CACHE_FS_LAYOUT = False


class FatalError(BaseException):

    def __init__(self, msg):
        super(FatalError, self).__init__()
        self.msg = msg

    def __str__(self):
        return "fatal: %s" % (self.msg,)


class NotAProject(FatalError):
    pass


class Ctrl(object):

    def __init__(self):
        self.root = self._find_root(os.getcwd())
        if self.root:
            self.config = self._load_config()

    def require_root(self, cmd):
        if cmd == "init":
            return
        if not self.root:
            raise NotAProject("Not a SchemaFS project (or any of the parent directories)")

    def pull(self, remote):
        pass

    def push(self, remote):
        pass

    def diff(self, view):
        dbs = self.config["databases"]
        result = {}
        for db in dbs:
            past = json.load(open(_pj(self.root, DIR_CACHE_WORKING_SCHEMA, '%s.json' % db)))
            result[db] = schema.diff(self.fs_to_struct(db), past)
        return view(result)

    def init(self, directory, server, user, db, use_existing):
        self.root = os.getcwd()
        if not use_existing:
            raise NotImplementedError("Init without existing server is not supported yet")
        if os.path.isdir(DIR_PROJECT):
            # todo: reinit
            return
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
            self.config = data
        for db_name in db:
            dumped = schema.dump(server, user, db_name).read()
            with open(_pj(DIR_DUMPS_WORKING, '%s.sql' % db_name), 'w') as working:
                working.write(dumped)
            struct = schema.parse_dump(dumped)
            with open(_pj(DIR_CACHE_WORKING_SCHEMA, "%s.json" % db_name), 'w') as cache:
                cache.write(json.dumps(struct))
            self.struct_to_fs(db_name, struct)

    # todo: this functions belongs to some other module - like fs.py
    def struct_to_fs(self, db, struct):
        db_root = _pj(self.root, self.config["directory"], db)
        os.makedirs(db_root)
        for t in struct.keys():
            directory = _pj(db_root, t)
            os.mkdir(directory)
            for name, definition in struct[t].items():
                with open(_pj(directory, '%s.sql' % name), 'w') as fl:
                    fl.write(definition)
        if CACHE_FS_LAYOUT:
            shutil.copytree(db_root, _pj(DIR_CACHE_WORKING_FS, db))

    def fs_to_struct(self, db):
        db_root = _pj(self.root, self.config["directory"], db)
        schema = {
            "functions": {},
            "tables": {}
        }
        for t in schema.keys():
            directory = _pj(db_root, t)
            if not os.path.isdir(directory):
                continue
            for g in iglob(_pj(directory, "*.sql")):
                name = os.path.splitext(os.path.basename(g))[0]
                schema[t][name] = open(g).read()
        return schema

    def clone(self):
        pass

    def _find_root(self, cwd):
        if os.path.isdir(_pj(cwd, DIR_PROJECT)):
            return cwd
        pardir = os.path.abspath(_pj(cwd, os.pardir))
        if pardir == cwd:
            return None
        return self._find_root(pardir)

    def _load_config(self):
        return json.load(open(_pj(self.root, DIR_PROJECT, 'config.json')))


def diff_view(diffs):
    for diff in diffs:
        for t, changes in diff.items():
            print t.toupper()
            for change, names in changes.items():
                print change, names

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
diff_parser.set_defaults(cmd='diff', view=diff_view)


if __name__ == '__main__':
    args = parser.parse_args()
    cli = Ctrl()
    kwargs = vars(args)
    cmd = kwargs['cmd']
    del kwargs['cmd']
    cli.require_root(cmd)
    getattr(cli, cmd)(**kwargs)
