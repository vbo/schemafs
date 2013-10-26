def drop_sql(obj):
    return "DROP TABLE %s;" % (obj["name"],)


def create_sql(obj):
    return obj["definition"]

def add_column_sql(table_name, new_col):
    tmp_str = ""
    if not new_col["nullable"]:
        tmp_str = "NOT NULL"
    if new_col["default"] is not None:
        if tmp_str != "":
            tmp_str += " "
        tmp_str += "DEFAULT '%s'" % new_col["default"]
    result = "ALTER TABLE %s ADD COLUMN %s %s %s" % (table_name, new_col["name"], new_col["type"], tmp_str)
    result = result.strip() + ';'
    return result


def change_sql(old_obj, new_obj):
    if old_obj["name"] != new_obj["name"]:
        return "ALTER TABLE %s RENAME TO %s;" % (old_obj["name"], new_obj["name"])
    if len(old_obj["columns"]) < len(new_obj["columns"]):
        for column in new_obj["columns"]:
            if column not in old_obj["columns"]:
                return add_column_sql(old_obj["name"], column)
    pass

