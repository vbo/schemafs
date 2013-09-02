from nose.tools import ok_, eq_
from .. import schema


def _test_func(name, definition):
    # todo: test_func* tests must go to test_parser (and some - must be deleted)
    struct = schema.parse_dump(definition)
    ok_(name in struct["functions"], "%s parsed as function" % name)
    eq_(definition, struct["functions"][name]["definition"])


def test_func_parser_dollar_quoted_good():
    _test_func("good", """
        CREATE FUNCTION good() RETURNS integer
        AS $$
            SELECT 1;
        $$
        LANGUAGE SQL;
    """.strip())


def test_func_parser_dollar_quoted_oneliner():
    _test_func("oneliner", """CREATE FUNCTION oneliner() RETURNS integer AS $$ SELECT 1; $$ LANGUAGE SQL""")


def test_func_parser_dollar_quoted_tagged():
    _test_func("tagged",  """
        CREATE FUNCTION tagged(in int, out f1 int, out f2 text) RETURNS integer
        AS $tag02$
            SELECT 1;
        $tag02$ LANGUAGE SQL;
    """.strip())


def test_func_parser_string_quoted():
    _test_func("str",  """
        CREATE FUNCTION str() RETURNS integer
        AS '
            SELECT 1;
        '
        LANGUAGE SQL;
    """.strip())
    _test_func("quote",  """
        CREATE FUNCTION quote() RETURNS text
        AS '
            SELECT ''1'';
        '
        LANGUAGE SQL;
    """.strip())
    _test_func("quote_oneliner",  (
        """CREATE FUNCTION quote_oneliner() RETURNS integer """
        """AS 'SELECT ''1'';' LANGUAGE SQL;"""
    ).strip())


def test_booktown():
    d1 = open('fixture/parser/booktown.sql', 'r')
    struct = schema.parse_dump(d1)
    ok_(len(struct["tables"]), "some tables parsed")
    ok_("publishers" in struct["tables"], "publishers table parsed")
    ok_(len(struct["functions"]), "some functions parsed")
    ok_("audit_bk" in struct["functions"])
