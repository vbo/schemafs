def drop_sql(obj):
    return "DROP FUNCTION %s(%s);" % (
        obj["name"], _arg_list(obj["arguments"])
    )


def create_sql(obj):
    return obj["definition"]


def change_sql(old_obj, new_obj):
    pass


def _arg_list(args):
    return ",".join(a["type"] for a in args)
