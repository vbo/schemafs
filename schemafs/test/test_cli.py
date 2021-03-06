import os
import shutil
from nose.tools import ok_, eq_, raises
from nose.plugins.attrib import attr
import re

from .. import cli
from .. import schema
from .. import differ


# todo: test cli view separately (pretty diff, output messages etc)
_s = '.unittest-sandbox'
_db_e = 'schemafs-test-existing'
_prepare_db_sql = """
    CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);
    CREATE FUNCTION test_func(integer) RETURNS integer LANGUAGE plpgsql AS $$
        DECLARE
        BEGIN
            RETURN 1;
        END;
    $$;
"""

isdir = os.path.isdir
exists = os.path.exists

@attr('network')
class TestCli:
    def setup(self):
        if isdir(_s):
            shutil.rmtree(_s)
        os.mkdir(_s)
        os.chdir(_s)

    def teardown(self):
        os.chdir(os.pardir)
        shutil.rmtree(_s)

    def test_find_root(self):
        # todo: test it with symlinks etc
        eq_(cli.Ctrl().root, None)
        os.makedirs("test/find/root")
        try:
            os.chdir("test/find")
            cli.Ctrl().init('sql', 'localhost', 'vbo', [_db_e], True)
            root_path = os.getcwd()
            try:
                os.chdir('root')
                eq_(cli.Ctrl().root, root_path)
            finally:
                os.chdir(os.pardir)
        finally:
            os.chdir(os.pardir)
            os.chdir(os.pardir)

    def test_cli_init(self):
        ctrl = cli.Ctrl()
        ctrl.init('sql', 'localhost', 'vbo', [_db_e], True)
        eq_(cli.Ctrl().root, os.getcwd())
        # todo: dehardcode pathes
        ok_(isdir('.schemafs'), "project directory created")
        ok_(exists('.schemafs/config.json'), "config file created")
        # todo: it needs to be in test_cli_refresh
        ok_(isdir('.schemafs/dumps/working'), "dumps dir created")
        ok_(exists('.schemafs/dumps/working/%s.sql' % _db_e), "dump saved")
        ok_(isdir('sql'), "root dir created")
        ok_(isdir('sql/%s/functions' % _db_e) and isdir('sql/%s/tables' % _db_e),
            "func and table dirs created")
        ok_(exists('sql/%s/tables/test_table.sql' % _db_e), "tables seems synced")
        ok_(exists('sql/%s/functions/test_func.sql' % _db_e), "funcs seems synced")

    def test_cli_diff(self):
        # todo: test _fs_to_struct separately
        ctrl = cli.Ctrl()
        ctrl.init('sql', 'localhost', 'vbo', [_db_e], True)
        diff = cli.Ctrl().diff()
        ok_(differ.diff_empty(diff[0][_db_e]))
        func = open('sql/%s/functions/test_func.sql' % _db_e).read()
        func = re.sub(r'(return\s+)(\d+);', r'\1\2\2;', func, flags=re.IGNORECASE)
        open('sql/%s/functions/test_func.sql' % _db_e, 'w').write(func)
        os.remove('sql/%s/tables/test_table.sql' % _db_e)
        ctrl.diff(lambda d, x, y: "test_func" in d[_db_e]["functions"]["changed"])
        ctrl.diff(lambda d, x, y: "test_table" in d[_db_e]["tables"]["removed"])
        # exit with non-empty diff - refresh tests rely on it

    @raises(cli.RefreshError)
    def test_cli_refresh_raise(self):
        self.test_cli_diff()
        cli.Ctrl().refresh()

    def test_cli_refresh(self):
        self.test_cli_diff()
        cli.Ctrl().refresh(force=True)
        diff = cli.Ctrl().diff()
        ok_(differ.diff_empty(diff[0][_db_e]))
