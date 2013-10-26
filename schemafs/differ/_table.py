def drop_sql(obj):
    return "DROP TABLE %s;" % (obj["name"],)


def create_sql(obj):
    return obj["definition"]


def change_sql(old_obj, new_obj):
    pass

