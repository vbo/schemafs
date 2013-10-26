from .. import schema
from . import _function
from . import _table

differs = {
    "functions": _function,
    "tables": _table
}


def diff(new, old):
    result = {}
    for key in schema.create_template():
        result[key] = _diff_dict(new.get(key, {}), old.get(key, {}))
        add_sql(differs[key], result[key])
    return result


def diff_empty(diff):
    for k, v in diff.items():
        for change, keys in v.items():
            if keys:
                return False
    return True


def _diff_dict(new, old):
    new_keyset = set(new.keys())
    old_keyset = set(old.keys())
    common_keyset = new_keyset.intersection(old_keyset)
    added_keyset = new_keyset - common_keyset
    removed_keyset = old_keyset - common_keyset
    changed_keyset = set(filter(lambda x: new[x]["definition"] != old[x]["definition"], common_keyset))
    return {
        # kludge: needs OOP here I think
        "added": [{"key": o, "new": new[o], "old": None} for o in added_keyset],
        "removed": [{"key": o, "new": None, "old": old[o]} for o in removed_keyset],
        "changed": [{"key": o, "new": new[o], "old": old[o]} for o in changed_keyset],
    }


def add_sql(differ, diff_result):
    for detail in diff_result["added"]:
        detail["sql"] = differ.create_sql(detail["new"])
    for detail in diff_result["removed"]:
        detail["sql"] = differ.drop_sql(detail["old"])
    for detail in diff_result["changed"]:
        detail["sql"] = differ.change_sql(detail["new"], detail["old"])


