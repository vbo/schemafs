from nose.tools import ok_, eq_
from .. import differ
from copy import deepcopy
from ..differ import _function


test_function = {"test_function":{
    "body":"$$\nBEGIN\n    RETURN QUERY(SELECT * FROM shr._shr_init_roles(nsp_name));\nEND;\n$$",
    "definition":"""CREATE FUNCTION test_function(nsp_name character varying) RETURNS SETOF character varying
        LANGUAGE plpgsql
        AS $$
            BEGIN
                RETURN QUERY(SELECT * FROM shr._shr_init_roles(nsp_name));
            END;
        $$;""".strip(),
    "name":"test_function",
    "returns":"""SETOF character varying
        LANGUAGE plpgsql""",
    "arguments":[
        {
            "default":None,
            "type":"character varying",
            "mode":None,
            "name":"nsp_name"
        }
    ],
    "attributes":""
}}

def test_function_renamed_sql():
    test_function2 = deepcopy(test_function)
    test_function2["test_function"]["name"] = "test_function2"
    sql = _function.change_sql(test_function["test_function"], test_function2["test_function"])
    ok_(sql == "ALTER FUNCTION test_function(character varying) RENAME TO test_function2;")

def test_function_drop_sql():
    sql = _function.drop_sql(test_function["test_function"])
    ok_(sql == "DROP FUNCTION test_function(character varying);")

def test_function_create_sql():
    sql = _function.create_sql(test_function["test_function"])
    ok_(sql == """CREATE FUNCTION test_function(nsp_name character varying) RETURNS SETOF character varying
        LANGUAGE plpgsql
        AS $$
            BEGIN
                RETURN QUERY(SELECT * FROM shr._shr_init_roles(nsp_name));
            END;
        $$;""".strip())