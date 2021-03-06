from nose.tools import ok_, eq_
from .. import differ
from copy import deepcopy
from ..differ import _table

test_table = {"test_table": {
        "constrains":{},
        "inherits":{},
        "name":"test_table",
        "definition": """
                        CREATE TABLE test_table (
                            id bigint NOT NULL,
                            email character varying NOT NULL,
                        );""".strip(),
        "tablespace": None,
        "with": None,
        "columns": [
            {
                "default": None,
                "type":"bigint",
                "name":"id",
                "nullable": False
            },
            {
                "default":None,
                "type":"character varying",
                "name":"email",
                "nullable":False
            }
        ]
    }
}

def test_table_column_added_sql():
    test_table2 = deepcopy(test_table)
    test_table2["test_table"]["columns"].append({
        "default":"",
        "type":"character varying",
        "name":"nickname",
        "nullable":False
    })
    sql = _table.change_sql(test_table["test_table"], test_table2["test_table"])
    ok_(sql == "ALTER TABLE test_table ADD COLUMN nickname character varying NOT NULL DEFAULT '';")

    test_table2 = deepcopy(test_table)
    test_table2["test_table"]["columns"].append({
        "default":None,
        "type":"character varying",
        "name":"nickname",
        "nullable":False
    })
    sql = _table.change_sql(test_table["test_table"], test_table2["test_table"])
    ok_(sql == "ALTER TABLE test_table ADD COLUMN nickname character varying NOT NULL;")

    test_table2 = deepcopy(test_table)
    test_table2["test_table"]["columns"].append({
        "default":None,
        "type":"character varying",
        "name":"nickname",
        "nullable":True
    })
    sql = _table.change_sql(test_table["test_table"], test_table2["test_table"])
    ok_(sql == "ALTER TABLE test_table ADD COLUMN nickname character varying;")

    test_table2 = deepcopy(test_table)
    test_table2["test_table"]["columns"].append({
        "default":'123123',
        "type":"character varying",
        "name":"nickname",
        "nullable":True
    })
    sql = _table.change_sql(test_table["test_table"], test_table2["test_table"])
    ok_(sql == "ALTER TABLE test_table ADD COLUMN nickname character varying DEFAULT '123123';")



def test_table_renamed_sql():
    test_table2 = deepcopy(test_table)
    test_table2["test_table"]["name"] = "test_table2"
    sql = _table.change_sql(test_table["test_table"], test_table2["test_table"])
    ok_(sql == "ALTER TABLE test_table RENAME TO test_table2;")


def test_table_drop_sql():
    sql = _table.drop_sql(test_table["test_table"])
    ok_(sql == "DROP TABLE test_table;")


def test_table_create_sql():
    sql = _table.create_sql(test_table["test_table"])
    ok_(sql == """
                        CREATE TABLE test_table (
                            id bigint NOT NULL,
                            email character varying NOT NULL,
                        );""".strip())


def test_table_changed_all():
    test_table2 = deepcopy(test_table)
    test_table2["test_table"]["name"] = "test_table111111111111111"
    test_table2["test_table"]["definition"] = """CREATE TABLE test_table (
                            id bigint NOT NULL,
                            email character varying NOT NULL,
                        );""".strip(),
    diff = differ.diff({"tables": test_table }, {"tables": test_table2 })
    ok_(diff["tables"]["changed"][0]["sql"] == "ALTER TABLE test_table RENAME TO test_table111111111111111;")
