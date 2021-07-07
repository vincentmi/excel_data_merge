import json

enumList = {
    "client_status": {"潜在客户": 1, "初步接触": 2, "持续跟进": 3, "成交客户": 4, "忠诚客户": 5, "无效客户": 6},
    "client_type": {"研学": 1, "_": 2},
    "bool": {"true": 1, "1": 1, "是": 1, "_": 0, "false": 0, "否": 0},
    "attitube": {"赞成": 1, "中立": 2, "反对": 3},
    "role": {"校长": 1, "副校长": 2, "年级主任": 3, "德育主任": 4, "教导主任": 5, "家委会": 6},
    "traffic": {"交通便利": 1, "路况不佳": 2, "位置偏僻": 3},
    "area": {"乡村": 1, "城镇": 2, "市区": 3},
    "grade": {"小学1年级": 1, "小学2年级": 2, "小学3年级": 3, "小学4年级": 4, "小学5年级": 5, "小学6年级": 6,
              "初中1年级": 7, "初中2年级": 8, "初中3年级": 9, "高中1年级": 10, "高中2年级": 11, "高中3年级": 12},
    "month": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "12": 12},
    "travel_type": {"地理类": 1, "自然类": 2, "历史类": 3, "科技类": 4, "人文类": 5, "体验类": 6},
    "income": {"20万元以上": 1, "15万元-20万元": 2, "10万元-15万元": 3, "5万元-10万元": 4, "5万元": 5},
    "decision_relation": {"信息提供者": 1, "决策人": 2, "重大影响者": 3, "反对者": 4, "普通人": 5},
    "intention": {"周边": 1, "省内": 2, "省外": 3, "国际": 4},
    "client_level": {"小型": 1, "中型": 2, "大型": 3, "A": 4, "B": 5, "C": 6},
    "school_system": {"小学": 1, "初级中学": 2, "高级中学": 3, "完全中学": 4, "九年一贯制学校": 5, "十二年一贯制学校": 6},
    "gender": {"男": 1, "女": 0},
    "position": {"校长": 1, "副校长": 2, "年级主任": 3, "德育主任": 4, "教导主任": 5, "家委会": 6},
    "star": {"1星": 1, "2星": 2, "3星": 3, "4星": 4, "5星": 5},
    "character": {"内敛型": 1,"开朗型": 2, "直接型": 3, "温和型": 4, "暴躁且排斥型":5 },
    "follow_type": { "当面拜访":1 ,"电话拜访":2 ,"即时通讯":3 }

}


def match(title, v):
    v = v.strip()
    if enumList.__contains__(title):
        if enumList[title].__contains__(v):
            return enumList[title][v]
        else:
            if enumList[title].__contains__("_"):
                return enumList[title]["_"]
            else:
                return None


def multi(title, v, sep="|"):
    v = v.strip()
    if v == "":
        return None
    else:
        items = []
        for item in v.split(sep):
            item_id = match(title, item)
            # print(item_id)
            if item_id is not None:
                items.append(str(item_id))

        if len(items) == 0:
            return None
        else:
            return json.dumps(items)
