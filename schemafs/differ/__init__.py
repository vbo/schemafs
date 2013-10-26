from .. import schema


def diff(left, right):
    result = {}
    for key in schema.create_template():
        result[key] = _diff_dict(left.get(key, {}), right.get(key, {}))
    return result


def diff_empty(diff):
    for k, v in diff.items():
        for change, keys in v.items():
            if keys:
                return False
    return True


def _diff_dict(left, right):
    left_keyset = set(left.keys())
    right_keyset = set(right.keys())
    common_keyset = left_keyset.intersection(right_keyset)
    return {
        "added": left_keyset - common_keyset,
        "removed": right_keyset - common_keyset,
        "changed": set(filter(lambda x: left[x]["definition"] != right[x]["definition"], common_keyset))
    }


