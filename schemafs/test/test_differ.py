from nose.tools import ok_, eq_
from .. import differ

def test_differ_changed():
    diff = differ.diff({
        "tables": {
            "test_table": {
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
    }, {
        "tables": {
            "test_table": {
                "constrains":{},
                "inherits":{},
                "name":"test_table111111111111111",
                "definition": """
                    CREATE TABLE test_table111111111111111 (
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
    })
    ok_(len(diff["tables"]["changed"]) == 1)
    ok_(diff["tables"]["changed"][0]["sql"] == "ALTER TABLE test_table RENAME TO test_table111111111111111;")
    ok_(not diff["tables"]["added"])
    ok_(not diff["tables"]["removed"])

