from nose.tools import ok_, eq_
from .. import schema


def test_diff_empty():
    diff = schema.diff({
        "functions": {
            "test_func": {"definition": """
                aaa
            """.strip()}
        }
    }, {
        "functions": {
            "test_func": {"definition": """
                aaa
            """.strip()}
        }
    })
    ok_(schema.diff_empty(diff))


def test_diff_changed():
    diff = schema.diff({
        "functions": {
            "test_func": {"definition": """
                aaa
            """.strip()}
        }
    }, {
        "functions": {
            "test_func": {"definition": """
                bbb
            """.strip()}
        }
    })
    ok_(len(diff["functions"]["changed"]) == 1)
    ok_(not diff["functions"]["added"])
    ok_(not diff["functions"]["removed"])


def test_diff_added_untouched_removed():
    diff = schema.diff({
        "functions": {
            "test_func_added": {"definition": """
                aaa
            """.strip()},
            "test_func": {"definition": """
                aaa
            """.strip()}
        }
    }, {
        "functions": {
            "test_func": {"definition": """
                aaa
            """.strip()},
            "test_func_removed": {"definition": """
                bbb
            """.strip()}
        }
    })["functions"]
    ok_("test_func_added" in diff["added"])
    union = reduce(lambda x, y: x.union(y), (diff["added"], diff["changed"], diff["removed"]))
    ok_(len(union) == 2)
    ok_("test_func" not in union)
    ok_("test_func_removed" in diff["removed"])
