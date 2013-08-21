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
    eq_(parsed["name"], "abc_schema.\"abc\"")
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
