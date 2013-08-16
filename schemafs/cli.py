import json
import shutil
import argparse
import os
from glob import iglob
import difflib

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


class RefreshError(FatalError):
    pass


class Ctrl(object):

    def __init__(self):
        self.root = self._find_root(os.getcwd())
        if self.root:
            self.config = self._load_config()

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
        config = {
            'directory': directory,
            'server': server,
            'user': user,
            'databases': db,
        }
        with open(_pj(DIR_PROJECT, 'config.json'), 'w') as config_file:
            config_file.write(json.dumps(config, indent=4, separators=(',', ': ')) + "\n")
            self.config = config
        self.refresh(force=True)

    def refresh(self, force=False):
        if not force:
            diff, cur, past = self.diff()
            if not all(schema.diff_empty(x) for x in diff.values()):
                raise RefreshError("Can't refresh tree with changes. Commit your changes or add --force to override")
        for db_name in self.config["databases"]:
            dumped = schema.dump(self.config["server"], self.config["user"], db_name).read()
            with open(_pj(DIR_DUMPS_WORKING, '%s.sql' % db_name), 'w') as working:
                working.write(dumped)
            struct = schema.parse_dump(dumped)
            with open(_pj(DIR_CACHE_WORKING_SCHEMA, "%s.json" % db_name), 'w') as cache:
                cache.write(json.dumps(struct))
            shutil.rmtree(_pj(self.root, self.config["directory"], db_name), ignore_errors=True)
            self.struct_to_fs(db_name, struct)

    def diff(self, view=None):
        dbs = self.config["databases"]
        result = {}
        current = {}
        past = {}
        for db in dbs:
            past[db] = json.load(open(_pj(self.root, DIR_CACHE_WORKING_SCHEMA, '%s.json' % db)))
            current[db] = self.fs_to_struct(db)
            result[db] = schema.diff(current[db], past[db])
        if hasattr(view, '__call__'):
            view(result, current, past)
        else:
            return result, current, past

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

    def _find_root(self, cwd):
        if os.path.isdir(_pj(cwd, DIR_PROJECT)):
            return cwd
        pardir = os.path.abspath(_pj(cwd, os.pardir))
        if pardir == cwd:
            return None
        return self._find_root(pardir)

    def _load_config(self):
        return json.load(open(_pj(self.root, DIR_PROJECT, 'config.json')))

    def require_root(self, cmd):
        if cmd == "init":
            return
        if not self.root:
            raise NotAProject("Not a SchemaFS project (or any of the parent directories)")


change_letters = {
    "added": "A",
    "removed": "R",
    "changed": "C"
}


def changes_view(changes, current, past):
    for change, names in changes.items():
        for name in names:
            print change_letters[change], name
            if change == "changed":
                diff = difflib.unified_diff(
                    a=past[name].splitlines(True),
                    b=current[name].splitlines(True),
                    fromfile="old",
                    tofile="new",
                )
                for line in diff:
                    print line,


def diff_view(diffs, current, past):
    for db, diff in diffs.items():
        for t, changes in diff.items():
            changes_view(changes, current[db][t], past[db][t])


# todo: declarative argparse
parser = argparse.ArgumentParser(prog='sfs')
subparsers = parser.add_subparsers()
init_parser = subparsers.add_parser('init')
init_arg = init_parser.add_argument
init_arg('--dir', dest='directory', nargs='?')
init_arg('--server', dest='server', nargs='?')
init_arg('--user', dest='user', nargs='?')
init_arg('--db', dest='db', nargs='*')
init_arg('--use-existing', dest='use_existing', action='store_true')
init_parser.set_defaults(cmd='init', directory='sql', server='localhost', user='postgres', db=None, use_existing=False)
refresh_parser = subparsers.add_parser('refresh')
refresh_parser.add_argument('--force', dest='force', action='store_true')
refresh_parser.set_defaults(cmd='refresh', force=False)
diff_parser = subparsers.add_parser('diff')
diff_parser.set_defaults(cmd='diff', view=diff_view)


if __name__ == '__main__':
    args = parser.parse_args()
    cli = Ctrl()
    kwargs = vars(args)
    cmd = kwargs['cmd']
    del kwargs['cmd']
    try:
        cli.require_root(cmd)
        getattr(cli, cmd)(**kwargs)
    except FatalError as e:
        print e
