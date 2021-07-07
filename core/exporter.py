import types


def print_row(row):
    for k in row:
        print(u"%s=%s" % (k, row[k]))


def make_index(data_array, key, value):
    index = {}
    for item in data_array:
        index[item[key]] = item[value]
    return index


# 导出数据
def mapper(sh, row_start, column_map, callback=None):
    row_id = row_start
    table_data = []
    for i in range(2, sh.nrows):
        row_id = row_id + 1
        row_data = {"id": row_id}
        for key in column_map:

            field_map = column_map[key]
            field_name = field_map["n"]
            value = sh.cell_value(i, key)
            # print(u"col{%s},value={%s}" % (key, value))

            # row_data["_" + field_name] = value

            if field_map.__contains__("v"):
                row_data[field_name] = field_map["v"]
            elif field_map.__contains__("f"):
                row_data[field_name] = field_map["f"](value)
            else:
                row_data[field_name] = value
        # print(type(callback))
        # print(types.FunctionType)
        if isinstance(callback, types.FunctionType):
            row_data = callback(row_data)

        table_data.append(row_data)

    return table_data


def print_header(sh, row, row2):
    for i in range(0, sh.ncols):
        print(u"%s %s=%s" % (i, sh.cell_value(row, i), sh.cell_value(row2, i)))


def print_data(data, id, field):
    print(u"id(%s) = %s" % (str(id), field))
    for item in data:
        if item["id"] == id:
            print(item[field])


def print_data_range(data, id_start, id_end, field):
    print(u"id(%s - %s) = %s" % (str(id_start), str(id_end), field))
    for item in data:
        if id_start <= item["id"] <= id_end:
            print(item[field])


def filter_by_field(data, field):
    new_data = []
    for row in data:
        if row[field] is None or row[field] == "":
            # print(u"not match - %s " % row[field])
            continue
        else:
            new_data.append(row)
    return new_data
