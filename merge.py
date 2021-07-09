import csv
import json
import time

import xlrd

from core import exporter, query
from core.exporter import write_file
from core.enum_util import match, multi

xls_client = "source/client.xls"
xls_contact = "source/contact.xls"
xls_follow = "source/follow.xls"

data_city = "source/data.csv"

sql_client = "out/client.sql"
sql_contact = "out/contact.sql"
sql_follow = "out/follow.sql"
sql_client_connect = "out/client_sale.sql"

indexClient = {}
srcCity = {
    10001: {"name": "四川", "parent": 0},
    10002: {"name": "成都", "parent": 10001},
    10003: {"name": "锦江区", "parent": 10002},
}
indexCity = json.load(open("out/area_index.json", "r"))

clientSalesConnect = []

defaultUser = 999
indexUser = {"黄江": 1,
             "米文书": 7,
             "丁天": 33,
             "陈靓艳": 34,
             "张军": 35,
             "熊博": 36,
             "梁智燊": 37,
             "胡润佳": 38,
             "黄贵添": 39,
             "林韵": 40,
             "张佩佩": 41,
             "李秋明": 42,
             "方燕娟": 43,
             "陈慧琳": 44,
             "杨宁": 45,
             "周烨玮": 46,
             "江瑞": 47,
             "许婷婷": 48,
             "唐章强": 49,
             "郝旻": 50,
             "马梦芸": 51,
             "杨顺富": 52,
             "陈松明": 53,
             "周芳": 54,
             "李成亮": 55,
             "曾娣": 56,
             "李林恒": 57,
             "孙绍光": 58,
             "邓潔": 59,
             "唐振华": 60,
             "殷杰": 61,
             "陈胡": 62,
             "曹琼琼": 63,
             "柏杰": 64,
             "李明昊": 65,
             "王彦明": 66,
             "杜鑫": 67,
             "王迎如": 68,
             "林潇君": 69,
             "丁楠": 70,
             "王嘉程": 71,
             "康翔宇": 72,
             "吴小丽": 73,
             "梁宇威": 74,
             "杨英": 75,
             "符婷婷": 76,
             "易雪": 77,
             "王露": 78,
             "李诚": 79,
             '谭忠鹏': 45,
             '康君': 33,
             '徐第萍': 58,
             '叶星辰': 62,
             '弓毓瑾': 62,
             '程金之': 62,
             '董慧': 45,
             '谢淼': 33,
             '章津萍': 45,
             '王楠': 33,
             '何泽明': 33,
             '魏成兵': 58,
             '潘希琳': 39,
             '廖燕': 33,
             '于骎': 33,
             '李彬': 33
             }

personQuit = {}

idGenMap = {}


def parse_time(v):
    if v.strip() != "":
        result = time.strptime(v, "%Y-%m-%d %H:%M")
        # print(u"parse_time(%s) -> %s" % (v, result))
        return result
    else:
        return None


def empty_str(v, default_str=""):
    if v is None or v.strip() == "":
        return default_str
    else:
        return v


def parse_date_preference(v):
    v = v.strip()
    if v is None:
        return None
    v = v.replace("-", " ").replace("月", "").replace("底", "").replace("初", "").replace("中", "") \
        .replace("，", " ").replace(",", " ").replace("-", " ").replace("；", " ").replace("、", " ")
    return multi("month", v, " ")


def parse_users(v):
    v = v.strip().replace(",", "|")
    users = []

    for item in v.split("|"):
        uid = parse_user(item)
        if uid is not None:
            users.append(str(uid))

    if len(users) > 0:
        # return json.dumps(users)
        return ",".join(users)
    else:
        return None


def parse_user(v):
    v = v.strip()
    if v is None or v == "":
        return defaultUser
    if indexUser.__contains__(v):
        return indexUser[v]
    else:
        personQuit[v] = 1
        return defaultUser


def parse_phone(v):
    phones = []
    v = v.replace("；", ";")
    v = v.replace("：", ":")
    splatted = v.split(";")
    for item in splatted:
        if item.strip() != "":
            phone = {}
            phone_meta = item.strip().split(":")
            if phone_meta[0] == "电话" or phone_meta[0] == "手机":
                phone["type"] = "PHONE"
                phone["no"] = phone_meta[1].strip()
            elif phone_meta[0] == "其他":
                phone["type"] = "OTHER"
                phone["no"] = phone_meta[1].strip()
            elif phone_meta[0] == "工作":
                phone["type"] = "WORK"
                phone["no"] = phone_meta[1].strip()
            phones.append(phone)

    # print(u"parse_phone(%s) -> %s" % (v, phones))
    if len(phones) > 0:
        return json.dumps(phones)
    else:
        return "[]";


def parse_number(v):
    index = v.find(".")
    if index != -1:
        v = v[0:index]
    if v is not None and v != "":
        return int(v)
    else:
        return None


def gen_id(gen_str):
    if idGenMap.__contains__(gen_str):
        gen_str_id = idGenMap.get(gen_str) + 1
    else:
        gen_str_id = 1
    idGenMap[gen_str] = gen_str_id
    return str.format("{:0>4d}", gen_str_id)


def guess_school_system(v):
    # print(v)
    system = []
    if v.find("小学") != -1:
        system.append(str(match("school_system", "小学")))
    elif v.find("中学") != -1:
        system.append(str(match("school_system", "初级中学")))
    elif v.find("九年") != -1:
        system.append(str(match("school_system", "九年一贯制学校")))
    elif v.find("高级中学") != -1:
        system.append(str(match("school_system", "高级中学")))
    elif v.find("初级中学") != -1:
        system.append(str(match("school_system", "初级中学")))
    elif v.find("中学") != -1:
        system.append(str(match("school_system", "完全中学")))
    elif v.find("学校") != -1:
        system.append(str(match("school_system", "九年一贯制学校")))
    else:
        system.append("1")
    return json.dumps(system)


def gen_client_code(row):
    # print(row["server_create_time"])
    time_str = time.strftime("%Y%m%d", row["server_create_time"])
    return "K" + time_str + gen_id("client_" + time_str)


# ##################### client

clientColumnMap = {
    0: {"n": "client_name"},
    1: {"n": "client_type", "f": lambda v: match("client_type", v)},
    2: {"n": "phone", "f": parse_phone},
    3: {"n": "client_status", "f": lambda v: match("client_status", v)},
    4: {"n": "content"},
    5: {"n": "province"},
    6: {"n": "city"},
    7: {"n": "area"},
    8: {"n": "address"},
    9: {"n": "yx_incharge_role", "f": lambda v: multi("role", v)},
    10: {"n": "decision_maker_name"},
    11: {"n": "decision_maker_tel"},
    12: {"n": "favor_yx_role", "f": lambda v: multi("role", v)},
    13: {"n": "disapproval_yx_role", "f": lambda v: multi("role", v)},
    14: {"n": "is_participate_yx", "f": lambda v: match("bool", v)},
    15: {"n": "school_attitude", "f": lambda v: match("attitube", v)},
    16: {"n": "local_policy_yx", "f": lambda v: match("bool", v)},
    17: {"n": "school_intention_yx", "f": lambda v: multi("intention", v)},
    18: {"n": "yx_decision_process"},
    19: {"n": "location_area", "f": lambda v: match("area", v)},
    20: {"n": "grades_num", "f": lambda v: parse_number(v)},
    21: {"n": "classes_num", "f": lambda v: parse_number(v)},
    22: {"n": "total_num", "f": lambda v: parse_number(v)},
    23: {"n": "record_proportion", "f": parse_number},
    24: {"n": "surrounding_traffic", "f": lambda v: match("traffic", v)},
    25: {"n": "can_travel_grade", "f": lambda v: multi("grade", v)},
    26: {"n": "can_travel_classes_num", "f": lambda v: parse_number(v)},
    27: {"n": "can_travel_total_num", "f": lambda v: parse_number(v)},
    28: {"n": "travel_date_preference", "f": parse_date_preference},
    29: {"n": "travel_days_preference", "f": lambda v: parse_number(v)},
    30: {"n": "garde_incharge_master"},
    31: {"n": "travel_type_preference", "f": lambda v: multi("travel_type", v)},
    32: {"n": "parent_avg_income", "f": lambda v: match("income", v)},
    33: {"n": "local_economy_lever"},
    34: {"n": "client_level", "f": lambda v: match("client_level", v)},
    35: {"n": "client_create_name"},
    36: {"n": "email"},
    37: {"n": "school_system", "f": lambda v: multi("school_system", v)},
    38: {"n": "sales", "f": parse_users},
    41: {"n": "last_follow_time", "f": parse_time},
    42: {"n": "last_follow_create_time", "f": parse_time},
    43: {"n": "server_create_time", "f": parse_time},
    44: {"n": "server_update_time", "f": parse_time}
}


def client_row_callback(row):
    row["client_code"] = gen_client_code(row)
    row["business_temp"] = 1
    row["client_create_id"] = parse_user(row["client_create_name"])
    row["create_id"] = row["client_create_id"]
    if row["school_system"] is None or row["school_system"] == "":
        row["school_system"] = guess_school_system(row["client_name"])
        # print(u"guessed -> %s" % (row["school_system"]))

    if row["address"] is None or row["address"] == "":
        row["address"] = " "

    # -----

    if row["area"] == "郫县":
        row["area"] = "郫都区"
    if row["area"] == "达县":
        row["area"] = "达川区"
    if row["province"] == "四川":
        row["province"] = "四川省"
    if row["area"] == "成都":
        row["city"] = "成都市"
    if row["city"] == "成都":
        row["city"] = "成都市"
    if row["area"] == "射洪县":
        row["area"] = "射洪市"
    if row["area"] == "双流县":
        row["area"] = "双流区"
    if row["province"] == "广西省" or row["province"] == "广西":
        row["province"] = "广西壮族自治区"

    city_id = []
    city_name = []
    if indexCity.__contains__(row["province"]):
        city_id.append(indexCity[row["province"]])
        city_name.append(row["province"])
    else:
        print(u"no-match %s" % row["province"])

    if indexCity.__contains__(row["city"]):
        city_id.append(indexCity[row["city"]])
        city_name.append(row["city"])
    else:
        print(u"no-match %s" % row["city"])

    if indexCity.__contains__(row["area"]):
        city_id.append(indexCity[row["area"]])
        city_name.append(row["area"])
    else:
        print(u"no-match %s" % row["area"])

    row["client_address_ids"] = json.dumps(city_id, ensure_ascii=False)
    row["client_address_names"] = json.dumps(city_name, ensure_ascii=False)

    del row["province"]
    del row["city"]
    del row["area"]

    # collect client sales connection
    if row["sales"] is not None and row["sales"] != "":
        for sale_id in row["sales"].split(","):
            connect = {
                "client_base_id": row["id"],
                "sale_id": sale_id
            }
            clientSalesConnect.append(connect)

    # print("{}", row)
    return row


def export_client(export_sql=False):
    wb_client = xlrd.open_workbook(xls_client)
    wb_sh = wb_client.sheet_by_index(0)
    print(u"%s - %d line, %d cols" % (xls_client, wb_sh.nrows, wb_sh.ncols))
    client_data = exporter.mapper(wb_sh, 1000, clientColumnMap, client_row_callback)


    # exporter.print_header(sh1, 1, 2)
    # exporter.print_row(data[0])

    client_index = exporter.make_index(client_data, "client_name", "id")

    struct_sql = "ALTER TABLE `client_basic_info` CHANGE `content` `content` VARCHAR(1024)  CHARACTER SET utf8mb4  COLLATE utf8mb4_general_ci  NULL  DEFAULT NULL  COMMENT '沟通内容详情';\n"
    struct_sql = struct_sql + "ALTER TABLE `client_basic_info` CHANGE `yx_decision_process` `yx_decision_process` VARCHAR(500)  CHARACTER SET utf8mb4  COLLATE utf8mb4_general_ci  NULL  DEFAULT NULL  COMMENT '研学活动决策流程';\n"
    struct_sql = struct_sql + "ALTER TABLE `client_basic_info` CHANGE `client_code` `client_code` CHAR(16)  CHARACTER SET utf8mb4  COLLATE utf8mb4_general_ci  NOT NULL  DEFAULT ''  COMMENT '客户编号';\n"
    sql = query.build_query(client_data, "client_basic_info", 100)

    if export_sql:
        write_file(sql_client, struct_sql + sql)
        write_file(sql_client_connect,query.build_query(clientSalesConnect, "client_sale", 100))

    return client_index


# exporter.print_data_range(data, 1181, 1194, "school_system")


# ##################### contact


def match_client_id(v):
    if indexClient.__contains__(v):
        return indexClient[v]
    else:
        return None


def contact_row_callback(row1):
    return row1


contactColumnMap = {
    0: {"n": "decision_relation", "f": lambda v: match("decision_relation", v)},
    1: {"n": "name"},
    # 2: {"n": "birthday", parse_time},
    8: {"n": "gender", "f": lambda v: match("gender", v)},
    11: {"n": "client_id", "f": match_client_id},
    12: {"n": "phone", "f": parse_phone},
    13: {"n": "dept"},
    14: {"n": "post", "f": lambda v: match("position", v)},
    15: {"n": "yx_affect_lever", "f": lambda v: match("star", v)},
    16: {"n": "email"},
    17: {"n": "wechat"},
    18: {"n": "hobby"},
    19: {"n": "character", "f": lambda v: multi("character", v)},
    20: {"n": "friendliness", "f": lambda v: match("star", v)},
    21: {"n": "promotion_demand", "f": lambda v: match("bool", v)},
    22: {"n": "remarks"},
    23: {"n": "create_id", "f": parse_user},
    24: {"n": "server_create_time", "f": parse_time},
    24: {"n": "server_update_time", "f": parse_time}
}


def export_contact(export_sql=False):
    # print(indexClient)
    wb_contact = xlrd.open_workbook(xls_contact)
    contact_sh = wb_contact.sheet_by_index(0)
    print(u"%s - %d line, %d cols" % (xls_contact, contact_sh.nrows, contact_sh.ncols))

    # print(contactColumnMap)
    # exporter.print_header(contact_sh, 1, 2)
    contact_data = exporter.mapper(contact_sh, 1000, contactColumnMap, contact_row_callback)
    # print(contact_data)
    contact_data = exporter.filter_by_field(contact_data, "client_id")

    # print(contact_data)

    struct_sql = ""
    sql = query.build_query(contact_data, "client_contacts_info", 100)
    if export_sql:
        write_file(sql_contact, struct_sql + sql)


# ######## 跟进记录


followColumnMap = {
    0: {"n": "name"},
    1: {"n": "follow_up_way", "f": lambda v: match("follow_type", v)},
    2: {"n": "follow_time", "f": parse_time},
    3: {"n": "question"},
    4: {"n": "content"},
    5: {"n": "feeling"},
    6: {"n": "address", "f": lambda v: empty_str(v, " ")},
    7: {"n": "create_id", "f": parse_user},
    8: {"n": "server_create_time", "f": parse_time},
    9: {"n": "server_update_time", "f": parse_time}
}


def follow_row_callback(row1):
    row1["update_id"] = defaultUser
    row1["clue_or_client"] = 1
    row1["subject_id"] = match_client_id(row1["name"])
    return row1


def export_follow(export_sql=False):
    wb_follow = xlrd.open_workbook(xls_follow)
    follow_sh = wb_follow.sheet_by_index(0)
    print(u"%s - %d line, %d cols" % (xls_follow, follow_sh.nrows, follow_sh.ncols))

    # print(contactColumnMap)
    # exporter.print_header(follow_sh, 1, 2)
    follow_data = exporter.mapper(follow_sh, 1000, followColumnMap, follow_row_callback)

    # print(follow_data)

    follow_data_filtered = exporter.filter_by_field(follow_data, "subject_id")

    struct_sql = "ALTER TABLE `follow_up` CHANGE `content` `content` VARCHAR(600)  CHARACTER SET utf8mb4  COLLATE utf8mb4_general_ci  NOT NULL  DEFAULT ''  COMMENT '说明/回答内容';"

    sql = query.build_query(follow_data_filtered, "follow_up", 100)
    if export_sql:
        write_file(sql_follow, struct_sql + sql)


indexClient = export_client(True)
export_contact(True)
export_follow(True)


print(personQuit)
