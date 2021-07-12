import json
from pypinyin import pinyin, Style
import core.query
from core.exporter import write_file

data = json.load(open("source/area.json"))

locationData = []

TYPE_PROVINCE = 3
TYPE_CITY = 2
TYPE_AREA = 4


def get_code(count):
    return "C" + "{:0>5d}".format(count)


def get_pinyin(name):
    pinyin_arr = pinyin(name, style=Style.NORMAL)
    pinyin_str = ""
    for char in pinyin_arr:
        pinyin_str = pinyin_str + char[0].title()
    return pinyin_str


def get_pinyin_short(name):
    pinyin_arr = pinyin(name, style=Style.INITIALS)
    pinyin_str = ""
    for char in pinyin_arr:
        pinyin_str = pinyin_str + char[0].upper()
    return pinyin_str


def create_record(count, id, name, parent_id, parent_level_name, type):
    short_code = get_pinyin_short(name)
    created_record = {
        "id": id,
        "code": get_code(count),
        "name_cn": name,
        "name_en": get_pinyin(name)[0:32],
        "parent_id": parent_id,
        "parent_level_name": parent_level_name,
        "short_code": short_code[0:3],
        "type": type,
        "status": 1,
        "is_deleted": 0,
        "create_id": 7,
        "server_create_time": "2021-06-08 14:43:00",
        "update_id": 7,
        "server_update_time": "2021-06-08 14:43:00"
    }
    return created_record


locationData.append({
        "id": 1,
        "code": "C0001",
        "name_cn": "中国",
        "name_en": "China",
        "parent_id": 0,
        "parent_level_name": "中国",
        "short_code": "CHA",
        "type": 1,
        "status": 1,
        "is_deleted": 0,
        "create_id": 7,
        "server_create_time": "2021-06-08 14:43:00",
        "update_id": 7,
        "server_update_time": "2021-06-08 14:43:00"
    })

countP = 0
item_count = 1

for province in data:
    print(u"%s(%s)" % (province["name"], province["code"]))
    item_count = item_count + 1
    record = create_record(item_count, province["code"], province["name"], 1, "中国", TYPE_PROVINCE)

    locationData.append(record)

    for city in province["children"]:
        item_count = item_count + 1
        record = create_record(item_count, city["code"], city["name"],
                               province["code"], "中国/" + province["name"], TYPE_CITY)

        locationData.append(record)

        print(u"  %s(%s)" % (city["name"], city["code"]))
        for area in city["children"]:
            print(u"    %s(%s)" % (area["name"], area["code"]))
            item_count = item_count + 1
            record = create_record(item_count, area["code"], area["name"], city["code"], "中国/"
                                   + province["name"] + "/" + city["name"], TYPE_AREA)
            locationData.append(record)

    countP = countP + 1

print(locationData)

print(countP)

sql = core.query.build_query(locationData, "hiseas_location", 100)

rIndex = {}
for item in locationData:
    rIndex[item["name_cn"]] = item["id"]

write_file("out/area_index.json", json.dumps(rIndex, ensure_ascii=False))
write_file("out/area.sql", sql)
