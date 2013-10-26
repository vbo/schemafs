from nose.tools import ok_, eq_
from .. import differ


def test_diff_empty():
    diff = differ.diff({
        "functions": {
            "test_func": {
                "name": "test_func",
                "definition": """
                aaa
            """.strip()}
        }
    }, {
        "functions": {
            "test_func": {
                "name": "test_func",
                "definition": """
                aaa
            """.strip()}
        }
    })
    ok_(differ.diff_empty(diff))


def test_diff_changed():
    diff = differ.diff({
        "functions": {
            "test_func": {
                "name": "test_func",
                "definition": """
                aaa
            """.strip()}
        }
    }, {
        "functions": {
            "test_func": {
                "name": "test_func",
                "definition": """
                bbb
            """.strip()}
        }
    })
    ok_(len(diff["functions"]["changed"]) == 1)
    ok_(not diff["functions"]["added"])
    ok_(not diff["functions"]["removed"])


def test_diff_added_untouched_removed():
    diff = differ.diff({
        "functions": {
            "test_func_added": {
                "name": "test_func_added",
                "arguments": [],
                "definition": """
                    aaa
                """.strip()},
            "test_func": {"definition": """
                aaa
            """.strip()}
        }
    }, {
        "functions": {
            "test_func": {
                "name": "test_func",
                "arguments": [],
                "definition": """
                    aaa
                """.strip()},
            "test_func_removed": {
                "name": "test_func",
                "arguments": [],
                "definition": """
                    bbb
                """.strip()}
        }
    })["functions"]
    def diff_keys(diff):
        return set([o["key"] for o in diff])
    ok_("test_func_added" in diff_keys(diff["added"]))
    union = reduce(lambda x, y: x.union(y), (diff_keys(diff["added"]), diff_keys(diff["changed"]), diff_keys(diff["removed"])))
    ok_(len(union) == 2)
    ok_("test_func" not in union)
    ok_("test_func_removed" in diff_keys(diff["removed"]))
