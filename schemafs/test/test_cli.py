import os, os.path
import shutil
from nose.tools import ok_, eq_

from .. import cli


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

def setup():
    if os.path.isdir(_s):
        pass
        shutil.rmtree(_s)
    os.mkdir(_s)
    os.chdir(_s)


def teardown():
    os.chdir('../')
    shutil.rmtree(_s)


def test_cli_init():
    ctrl = cli.Ctrl()
    ctrl.init('sql', 'localhost', 'vbo', [_db_e], True)
    ok_(os.path.isdir('.schemafs'), "project directory created")
    ok_(os.path.exists('.schemafs/config.json'), "config file created")
    ok_(os.path.isdir('.schemafs/dumps/working'), "dumps dir created")
    ok_(os.path.exists('.schemafs/dumps/working/%s.sql' % _db_e), "dump saved")
    ok_(os.path.isdir('sql'), "root dir created")
    ok_(os.path.isdir('sql/%s/functions' % _db_e) and os.path.isdir('sql/%s/tables' % _db_e), "func and table dirs created")
    ok_(os.path.exists('sql/%s/tables/test_table.sql' % _db_e), "tables seems synced")
    ok_(os.path.exists('sql/%s/functions/test_func.sql' % _db_e), "funcs seems synced")

