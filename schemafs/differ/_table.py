def drop_sql(obj):
    return "DROP TABLE %s;" % (obj["name"],)


def create_sql(obj):
    return obj["definition"]


def change_sql(old_obj, new_obj):
    if (old_obj["name"] != new_obj["name"]):
        return "ALTER TABLE %s RENAME TO %s;" % (old_obj["name"], new_obj["name"])
    pass

