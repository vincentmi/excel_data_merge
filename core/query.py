import time


def quote(v):
    if isinstance(v, int):
        v = str(v)
    if v is None or v == "":
        v = "NULL"
    elif isinstance(v, str):
        v = "'" + v.replace("\'", "\\'").replace("\n", "\\n") + "'"
    elif isinstance(v, time.struct_time):
        v = "'" + time.strftime("%Y-%m-%d %H:%M:%S", v) + "'"
    else:
        v = "'"+str(v)+"'"
    return v


def build_query(source_data, table, batch_size=30):
    field_sql = "`,`".join(source_data[0].keys())
    field_sql = "`"+field_sql+"`"
    sql_prefix = "INSERT INTO `" + table + "` (" + field_sql + ") VALUES "
    batch_sql = ""
    batch_count = 0
    result_sql = ""
    for row in source_data:
        row_values = []
        for key in row:
            row_str = quote(row[key])
            row_values.append(row_str)
        batch_sql = batch_sql + "\n(" + ",".join(row_values) + "),"
        batch_count = batch_count + 1
        if batch_count >= batch_size:
            result_sql = result_sql + sql_prefix + batch_sql[0:len(batch_sql) - 1] + "\n;\n"
            batch_sql = ""
            batch_count = 0
    if batch_count > 0:
        result_sql = result_sql + sql_prefix + batch_sql[0:len(batch_sql) - 1] + "\n;\n"

    return result_sql
