from nose.tools import ok_, eq_
from .. import schema


def _test_func(name, definition):
    struct = schema.parse_dump(definition)
    ok_(name in struct["functions"], "%s parsed as function" % name)
    eq_(definition, struct["functions"][name])


def test_func_parser_dollar_quoted_good():
    _test_func("good", """
        CREATE FUNCTION good()
        AS $$
            SELECT 1;
        $$
        LANGUAGE SQL;
    """.strip())


def test_func_parser_dollar_quoted_oneliner():
    _test_func("oneliner", """CREATE FUNCTION oneliner() AS $$ SELECT 1; $$ LANGUAGE SQL;""")


def test_func_parser_dollar_quoted_tagged():
    _test_func("tagged",  """
        CREATE FUNCTION tagged(in int, out f1 int, out f2 text)
        AS $tag02$
            SELECT 1;
        $tag02$ LANGUAGE SQL;
    """.strip())


def test_func_parser_string_quoted():
    _test_func("str",  """
        CREATE FUNCTION str()
        AS '
            SELECT 1;
        '
        LANGUAGE SQL;
    """.strip())
    _test_func("quote",  """
        CREATE FUNCTION quote()
        AS '
            SELECT ''1'';
        '
        LANGUAGE SQL;
    """.strip())
    _test_func("quote_oneliner",  """CREATE FUNCTION quote_oneliner() AS 'SELECT ''1'';' LANGUAGE SQL;""".strip())


def test_booktown():
    d1 = open('fixture/parser/booktown.sql', 'r')
    struct = schema.parse_dump(d1)
    ok_(len(struct["tables"]), "some tables parsed")
    ok_("publishers" in struct["tables"], "publishers table parsed")
    ok_(len(struct["functions"]), "some functions parsed")
    ok_("audit_bk" in struct["functions"])
