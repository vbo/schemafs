def drop_sql(obj):
    return "DROP FUNCTION %s(%s);" % (
        obj["name"], _arg_list(obj["arguments"])
    )


def create_sql(obj):
    return obj["definition"]


def change_sql(old_obj, new_obj):
    if old_obj["name"] != new_obj["name"]:
        return "ALTER FUNCTION %s(%s) RENAME TO %s;" % (
            old_obj["name"], _arg_list(old_obj["arguments"]), new_obj["name"]
        )
    pass


def _arg_list(args):
    return ",".join(a["type"] for a in args)
