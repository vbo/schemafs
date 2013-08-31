from nose.tools import ok_, eq_, raises, with_setup

from .. import parser


def test_create_table():
    # todo: unit-test BaseParser features separately
    stmt = """
        CREATE TABLE abc_schema."abc" (
            id bigint not null,
            name character varying default 'hello =)'::text,
            bca_id bigint not null,
            CONSTRAINT abc_bca_fkey FOREIGN KEY (bca_id)
                REFERENCES bca (id) MATCH SIMPLE
                ON UPDATE NO ACTION ON DELETE NO ACTION
        ) TABLESPACE disk01;
    """
    parsed = parser.CreateTableParser(stmt).parse()
    eq_(parsed["name"], 'abc_schema."abc"')
    ok_("abc_bca_fkey" in parsed["constrains"])
    eq_(parsed["tablespace"], "disk01")
    eq_(len(parsed["columns"]), 3)
    col_props_expected = [
        {"name": "id", "type": "bigint", "nullable": False},
        {"name": "name", "type": "character varying", "nullable": True, "default": "'hello =)'::text"},
        {"name": "bca_id", "type": "bigint", "nullable": False},
    ]
    for i, col in enumerate(col_props_expected):
        actual = parsed["columns"][i]
        for key in col:
            eq_(col[key], actual[key])


def test_create_function():
    body = """$$
        BEGIN
            RETURN a1;
        END;
    $$"""
    stmt = """
        CREATE FUNCTION abc(IN a1 integer)
        RETURNS integer AS """ + body + """ LANGUAGE plpgsql;
    """
    parsed = parser.CreateFunctionParser(stmt).parse()
    eq_(parsed["name"], "abc")
    eq_(parsed["returns"], "integer")
    eq_(parsed["body"], body)
    eq_(len(parsed["arguments"]), 1)
    arg = parsed["arguments"][0]
    eq_(arg["mode"], "IN")
    eq_(arg["name"], "a1")
    eq_(arg["type"], "integer")


def test_create_function_corners():
    body = """'
        select ''hello world''::text
    '"""
    stmt = """
        create function bcd(a1 text, a2 character varying, a3 timestamp with time zone)
        returns text as """ + body + """ language sql volatile;
    """
    parsed = parser.CreateFunctionParser(stmt).parse()
    eq_(parsed["returns"], "text")
    eq_(parsed["body"], body)
    eq_(len(parsed["arguments"]), 3)
    eq_(parsed["arguments"][1]["type"], "character varying")
    eq_(parsed["arguments"][2]["type"], "timestamp with time zone")
