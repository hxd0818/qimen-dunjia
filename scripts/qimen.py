#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奇门遁甲排盘解卦系统
支持：时家奇门排盘、格局分析、吉凶判断、破局建议
算法：置闰法（正统拆补法）
"""

import json
import sys
import math
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any

# ============================================================
# 基础数据定义
# ============================================================

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

PALACES = {
    1: {"name": "坎一宫", "trigram": "坎", "element": "水", "direction": "北"},
    2: {"name": "坤二宫", "trigram": "坤", "element": "土", "direction": "西南"},
    3: {"name": "震三宫", "trigram": "震", "element": "木", "direction": "东"},
    4: {"name": "巽四宫", "trigram": "巽", "element": "木", "direction": "东南"},
    5: {"name": "中五宫", "trigram": "中", "element": "土", "direction": "中央"},
    6: {"name": "乾六宫", "trigram": "乾", "element": "金", "direction": "西北"},
    7: {"name": "兑七宫", "trigram": "兑", "element": "金", "direction": "西"},
    8: {"name": "艮八宫", "trigram": "艮", "element": "土", "direction": "东北"},
    9: {"name": "离九宫", "trigram": "离", "element": "火", "direction": "南"},
}

SAN_QI_LIU_YI = {
    "戊": {"hidden": "甲子"}, "己": {"hidden": "甲戌"},
    "庚": {"hidden": "甲申"}, "辛": {"hidden": "甲午"},
    "壬": {"hidden": "甲辰"}, "癸": {"hidden": "甲寅"},
}
SAN_QI = ["乙", "丙", "丁"]

EIGHT_DOORS = {
    "开门": {"element": "金", "nature": "吉", "meaning": "开启、通达、事业、贵人"},
    "休门": {"element": "水", "nature": "吉", "meaning": "休息、和缓、洽谈、求财"},
    "生门": {"element": "土", "nature": "大吉", "meaning": "生机、财运、房产、谋利"},
    "伤门": {"element": "木", "nature": "凶", "meaning": "伤害、争斗、捕猎、激烈"},
    "杜门": {"element": "木", "nature": "平", "meaning": "隐藏、阻塞、技术、隐匿"},
    "景门": {"element": "火", "nature": "平", "meaning": "景象、文书、谋划、声名"},
    "死门": {"element": "土", "nature": "凶", "meaning": "死亡、终结、地产、旧事"},
    "惊门": {"element": "金", "nature": "凶", "meaning": "惊恐、诉讼、口舌、变动"},
}

NINE_STARS = {
    "天蓬": {"element": "水", "nature": "凶/暗助", "meaning": "大盗、智者、暗中行事"},
    "天任": {"element": "土", "nature": "小吉", "meaning": "农耕、稳重、持久"},
    "天冲": {"element": "木", "nature": "小吉", "meaning": "武士、冲动、雷厉风行"},
    "天辅": {"element": "木", "nature": "大吉", "meaning": "文官、教育、贵人"},
    "天英": {"element": "火", "nature": "平", "meaning": "武将、烈性、文书"},
    "天芮": {"element": "土", "nature": "凶", "meaning": "疾病、学生、问题"},
    "天柱": {"element": "金", "nature": "凶/小吉", "meaning": "破坏、说客、口才"},
    "天心": {"element": "金", "nature": "大吉", "meaning": "医者、将领、核心"},
    "天禽": {"element": "土", "nature": "吉", "meaning": "忠厚、中心、稳定"},
}

EIGHT_SPIRITS_YANG = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
EIGHT_SPIRITS_YIN = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]

SPIRIT_INFO = {
    "值符": {"nature": "大吉", "meaning": "统领百神、百事皆宜"},
    "腾蛇": {"nature": "凶/半凶", "meaning": "虚诈、怪异、缠绕"},
    "太阴": {"nature": "吉", "meaning": "隐匿、密谋、女人"},
    "六合": {"nature": "吉", "meaning": "和合、婚姻、合作"},
    "白虎": {"nature": "凶", "meaning": "争斗、血光、威权"},
    "玄武": {"nature": "凶/半凶", "meaning": "盗贼、暗昧、诈骗"},
    "九地": {"nature": "吉", "meaning": "屯兵、固守、柔顺"},
    "九天": {"nature": "吉", "meaning": "扬兵、飞升、进取"},
}

YANG_FLY_ORDER = [6, 7, 8, 9, 1, 2, 3, 4, 5]
YIN_FLY_ORDER = [6, 5, 4, 3, 2, 1, 9, 8, 7]

SHICHEN_HOURS = [(23,0),(1,3),(3,5),(5,7),(7,9),(9,11),
                 (11,13),(13,15),(15,17),(17,19),(19,21),(21,23)]

XUN_SHOU = {
    "甲子": ("戊", "子"), "甲戌": ("己", "戌"), "甲申": ("庚", "申"),
    "甲午": ("辛", "午"), "甲辰": ("壬", "辰"), "甲寅": ("癸", "寅"),
}
XUN_KONG_WANG = {
    "甲子": ["戌","亥"], "甲戌": ["申","酉"], "甲申": ["午","未"],
    "甲午": ["辰","巳"], "甲辰": ["寅","卯"], "甲寅": ["子","丑"],
}

JIEQI_JU = {
    "冬至": {"upper":1,"middle":7,"lower":4}, "小寒": {"upper":2,"middle":8,"lower":5},
    "大寒": {"upper":2,"middle":8,"lower":5}, "立春": {"upper":8,"middle":2,"lower":5},
    "雨水": {"upper":9,"middle":3,"lower":6}, "惊蛰": {"upper":1,"middle":7,"lower":4},
    "春分": {"upper":3,"middle":9,"lower":6}, "清明": {"upper":4,"middle":1,"lower":7},
    "谷雨": {"upper":4,"middle":1,"lower":7}, "立夏": {"upper":4,"middle":1,"lower":7},
    "小满": {"upper":5,"middle":2,"lower":8}, "芒种": {"upper":6,"middle":3,"lower":9},
    "夏至": {"upper":9,"middle":3,"lower":6}, "小暑": {"upper":8,"middle":2,"lower":5},
    "大暑": {"upper":8,"middle":2,"lower":5}, "立秋": {"upper":2,"middle":8,"lower":5},
    "处暑": {"upper":2,"middle":8,"lower":5}, "白露": {"upper":7,"middle":1,"lower":4},
    "秋分": {"upper":7,"middle":1,"lower":4}, "寒露": {"upper":6,"middle":9,"lower":3},
    "霜降": {"upper":6,"middle":9,"lower":3}, "立冬": {"upper":6,"middle":9,"lower":3},
    "小雪": {"upper":5,"middle":8,"lower":2}, "大雪": {"upper":4,"middle":7,"lower":1},
}

# 地盘基础排列
DIPAN_BASE = {}
for ju in range(1, 10):
    base = []
    if ju <= 5:
        start = ju
        for i in range(10):
            pos = (start + i - 1) % 9 + 1
            base.append(pos if pos != 5 else 5)
    else:
        start = ju
        for i in range(10):
            pos = start - i
            while pos <= 0: pos += 9
            base.append(pos if pos != 5 else 5)
    DIPAN_BASE[ju] = base

# 格局库（完整版）
GEJU_DB = [
    # === 大吉格 ===
    (["戊","丙"], "飞鸟跌穴", "大吉", "求财得财，百事皆宜，利求谋"),
    (["丙","戊"], "青龙返首", "吉", "吉事可成，利于进取，贵人相助"),
    # 三遁
    (None, "_tian_dun", "大吉", "生门+丙+休神：隐遁求安，宜守不宜攻"),
    (None, "_di_dun", "大吉", "生门+乙+六合：宜安营扎寨，避凶趋吉"),
    (None, "_yun_dun", "吉", "生门+丁+九地/太阴：宜隐蔽行事"),
    (None, "_feng_dun", "吉", "生门+乙+巽四宫：顺风而行，事半功倍"),
    (None, "_long_dun", "吉", "生门+乙/丁+乾/坎：宜涉水修造"),
    (None, "_hu_dun", "吉", "开门+乙+艮八宫：宜设伏捕猎"),
    (None, "_shen_dun", "大吉", "生门+丙+九天：如有神助"),
    (None, "_gui_dun", "平", "生门+丁+九地：宜侦探惑敌"),
    # 吉格
    (["乙","开"], "欢怡", "吉", "喜庆和合，婚姻大吉"),
    (["乙","休"], "欢怡", "吉", "喜庆和合，家庭和睦"),
    (["丁","休"], "和谐", "吉", "平和顺畅，宜和解谈判"),
    (["丙","开"], "相生", "吉", "光明通达，利于事业"),
    (["辛","休"], "见喜", "小吉", "有意外之喜，但防纠纷"),
    # 三奇得使
    (None, "_sanqi_deshi", "吉", "三奇临值符：奇门并至，百事亨通"),
    (None, "_yunv_shoumen", "吉", "丁奇临值使门：宜婚嫁宴请隐私事"),
    # === 大凶格 ===
    (["庚","戊"], "伏宫格", "大凶", "大祸将至，宜速避远走"),
    (["戊","庚"], "飞宫格", "大凶", "动荡不安，凶去不来亦不稳"),
    (["庚","庚"], "战格（格格）", "大凶", "同行相残，兄弟反目，血光之灾"),
    (["庚","壬"], "上格（移荡格）", "大凶", "行人不归，内外缠绵难解"),
    (["庚","癸"], "大格", "凶", "行人失约，官司败诉"),
    (["辛","乙"], "青龙逃走", "大凶", "奴仆拐带，钱财流失，破财伤人"),
    (["乙","辛"], "白虎猖狂", "大凶", "远行有灾，防刀剑之厄"),
    (["庚","丙"], "太白入荧", "凶", "贼来必获，但防口舌争斗"),
    (["丙","庚"], "荧入太白", "凶", "破财损夷，防意外灾难"),
    (["辛","乙"], "上屋抽梯", "凶", "进退两难，防被人出卖"),
    (["癸","丁"], "蛇夭矫", "凶", "虚假不实，防欺诈诅咒"),
    (["癸","丁"], "朱雀投江", "凶", "文书失落，音信难通"),
    (["丁","癸"], "雀入水", "凶", "是非口舌，奸诈暗生"),
    (["辛","丁"], "猪假虎威", "凶", "虚张声势，实为受制"),
    (["丁","辛"], "虎坐明堂", "凶/吉参半", "讼则有罪，问病则凶"),
    (["壬","庚"], "互格（阻格）", "凶", "男女相害，内外不和"),
    (["癸","庚"], "大格变体", "凶", "大事不成，小事亦凶"),
    (["癸","壬"], "复格（女旺男衰）", "凶/半凶", "阴盛阳衰，女性主导"),
    (["癸","癸"], "天网四张", "凶", "行动受阻，宜守不宜攻"),
    (["辛","辛"], "伏吟格", "凶", "停滞不通，万般困顿"),
    (["壬","壬"], "地罗蔽障", "凶", "晦暗不明，事多阻碍"),
    (["戊","戊"], "伏吟", "凶", "停滞不动，万事受阻"),
    (["己","己"], "地户逢鬼", "凶", "暗昧不明，小人暗算"),
    (["辛","戊"], "刑格", "凶", "讼狱被刑，防牢狱之灾"),
    (["己","庚"], "刑格遇格", "大凶", "官司刑狱，血光之灾"),
    (["庚","己"], "刑格变体", "凶", "疾病官非，需谨慎"),
    (["壬","辛"], "蛇相冲", "凶", "谋事多舛，反复不定"),
    (["辛","壬"], "腾蛇相缠", "凶", "纠缠不清，梦魇不安"),
    (["己","壬"], "地网高张", "凶", "狡诈欺蒙，犹疑不决"),
    (["壬","己"], "反覆", "凶", "进退维谷，反复无常"),
    (["己","癸"], "地刑玄武", "凶", "防被盗、被诉"),
    (["癸","己"], "华盖持势", "平/凶", "犯科遭究，需谨慎"),
    (["己","戊"], "明堂无恩", "凶", "失信于人，功亏一篑"),
    (["戊","己"], "入门遇户", "平/凶", "表面和合，内里不和"),
    (["己","丙"], "火悖地户", "凶", "祸从内起，防妇人"),
    (["丙","己"], "日月并明后悖", "平", "先明后暗，先成后败"),
    (["己","丁"], "地户朱雀", "平/吉", "文书有利，但防隐私泄露"),
    (["丁","己"], "女就利", "平", "阴人吉利，私情有碍"),
    (["己","辛"], "鬼退", "平/吉", "祸患渐消，但需主动"),
    (["辛","己"], "背势", "凶", "谋事不顺，力不从心"),
]


def get_ganzhi_year(year):
    return HEAVENLY_STEMS[(year-4)%10] + EARTHLY_BRANCHES[(year-4)%12]

def get_ganzhi_month(year, month):
    yg = HEAVENLY_STEMS[(year-4)%10]
    m = {"甲":2,"己":2,"乙":14,"庚":14,"丙":26,"辛":26,"丁":38,"壬":38,"戊":0,"癸":0}
    return HEAVENLY_STEMS[(m.get(yg,0)+month-1)%10] + EARTHLY_BRANCHES[(month+1)%12]

def get_ganzhi_day(year, month, day):
    base = datetime(2000,1,1)
    diff = (datetime(year,month,day)-base).days
    return HEAVENLY_STEMS[(4+diff)%10] + EARTHLY_BRANCHES[(6+diff)%12]

def get_shichen(hour):
    for i,(s,e) in enumerate(SHICHEN_HOURS):
        if s <= hour < e or (s>e and (hour>=s or hour<e)):
            return i
    return (hour+1)//2 % 12

def get_ganzhi_shichen(rigan, hour):
    idx = get_shichen(hour)
    zhi = EARTHLY_BRANCHES[idx]
    m = {"甲":0,"己":0,"乙":10,"庚":10,"丙":2,"辛":2,"丁":4,"壬":4,"戊":6,"癸":6}
    return HEAVENLY_STEMS[(m.get(rigan,0)+idx)%10] + zhi


class QimenChart:
    def __init__(self, year, month, day, hour, question=""):
        self.year = year; self.month = month; self.day = day
        self.hour = hour; self.question = question
        self.ganzhi_year = get_ganzhi_year(year)
        self.ganzhi_month = get_ganzhi_month(year, month)
        self.ganzhi_day = get_ganzhi_day(year, month, day)
        self.rigan = self.ganzhi_day[0]
        self.ganzhi_shichen = get_ganzhi_shichen(self.rigan, hour)
        self.ju_number = 0
        self.is_yang_dun = True
        self.yuan = ""
        self.current_jieqi = ""
        self.xun_shou = ""
        self.xun_yi = ""
        self.zhifu_palace = 0
        self.zhimen_palace = 0
        self.chart = {}
        self._setup()

    def _setup(self):
        self._determine_ju()
        self._dipan()
        self._tianpan()
        self._renpan()
        self._spirits()
        self._geju_analysis()

    def _determine_ju(self):
        jqs = {
            (1,6,8):"小寒",(1,21,8):"大寒",(2,4,6):"立春",(2,19,6):"雨水",
            (3,6,6):"惊蛰",(3,21,6):"春分",(4,5,6):"清明",(4,20,6):"谷雨",
            (5,6,6):"立夏",(5,21,6):"小满",(6,6,6):"芒种",(6,22,8):"夏至",
            (7,7,8):"小暑",(7,23,8):"大暑",(8,8,6):"立秋",(8,23,6):"处暑",
            (9,8,6):"白露",(9,23,6):"秋分",(10,8,6):"寒露",(10,24,6):"霜降",
            (11,8,6):"立冬",(11,22,6):"小雪",(12,7,8):"大雪",(12,22,8):"冬至",
        }
        best, min_d = "冬至", 999
        for (m,d,_), n in jqs.items():
            dd = abs(self.day-d)+abs(self.month-m)*30
            if dd < min_d: min_d, best = dd, n
        self.current_jieqi = best
        dp = self.day % 15
        self.yuan = "upper" if dp<=5 else ("middle" if dp<=10 else "lower")
        ji = JIEQI_JU.get(best, {"upper":1})
        self.ju_number = ji.get(self.yuan, 1)
        self.is_yang_dun = self.ju_number <= 5

    def _dipan(self):
        base = DIPAN_BASE[self.ju_number]
        yis = ["戊","己","庚","辛","壬","癸","乙","丙","丁"]
        for i, yi in enumerate(yis):
            p = base[i]
            self.chart.setdefault(p, self._new_palace(p))["dipan"] = yi
        self.chart.setdefault(5, self._new_palace(5))["dipan"] = "(寄坤二)"

    def _new_palace(self, p):
        return {"palace":p, "info":PALACES[p], "dipan":"", "tianpan":"",
                "renpan":"","shen":"","men":"","star":"","geju":[],"geju_level":""}

    def _tianpan(self):
        rg = self.ganzhi_day
        for xun, (yi, br) in XUN_SHOU.items():
            bi = EARTHLY_BRANCHES.index(br)
            for j in range(10):
                if EARTHLY_BRANCHES[(bi+j)%12] == rg[1]:
                    self.xun_shou, self.xun_yi = xun, yi
                    break
            if self.xun_shou: break
        if not self.xun_shou:
            self.xun_shou, self.xun_yi = "甲子", "戊"

        zbf = None
        for p, d in self.chart.items():
            if d["dipan"] == self.xun_yi:
                zbf = p; break
        if not zbf: zbf = self.ju_number

        sz = self.ganzhi_shichen[1]
        xbi = EARTHLY_BRANCHES.index(XUN_SHOU[self.xun_shou][1])
        cbi = EARTHLY_BRANCHES.index(sz)
        steps = cbi - xbi
        if steps < 0: steps += 12

        fo = YANG_FLY_ORDER if self.is_yang_dun else YIN_FLY_ORDER
        ci = next((i for i,p in enumerate(fo) if p==zbf), 0)
        self.zhifu_palace = fo[(ci+steps)%9]

        yis = ["戊","己","庚","辛","壬","癸","乙","丙","丁"]
        yii = yis.index(self.xun_yi) if self.xun_yi in yis else 0
        si = next((i for i,p in enumerate(fo) if p==self.zhifu_palace), 0)

        for i in range(9):
            fi = (si+i)%9 if self.is_yang_dun else (si-i)%9
            if fi<0: fi+=9
            p = fo[fi]
            ty = yis[(yii+i)%9]
            if p in self.chart:
                self.chart[p]["tianpan"] = ty

    def _renpan(self):
        fo = YANG_FLY_ORDER if self.is_yang_dun else YIN_FLY_ORDER
        doors = ["开门","休门","生门","伤门","杜门","景门","死门","惊门"]
        stars_list = ["天蓬","天任","天冲","天辅","天英","天芮","天柱","天心"]

        sz = self.ganzhi_shichen[1]
        xbi = EARTHLY_BRANCHES.index(XUN_SHOU[self.xun_shou][1])
        cbi = EARTHLY_BRANCHES.index(sz)
        msteps = cbi - xbi
        if msteps < 0: msteps += 12

        self.zhimen_palace = fo[(self.ju_number-1+msteps)%9]
        if self.zhimen_palace == 0: self.zhimen_palace = 9

        si = next((i for i,p in enumerate(fo) if p==self.zhimen_palace), 0)
        for i, door in enumerate(doors):
            fi = (si+i)%9 if self.is_yang_dun else (si-i)%9
            if fi<0: fi+=9
            p = fo[fi]
            if p in self.chart: self.chart[p]["men"] = door

        for i, star in enumerate(stars_list):
            fi = (si+i)%9 if self.is_yang_dun else (si-i)%9
            if fi<0: fi+=9
            p = fo[fi]
            if p in self.chart: self.chart[p]["star"] = star
        self.chart.setdefault(5,self._new_palace(5))["star"] = "天禽"

    def _spirits(self):
        sp = EIGHT_SPIRITS_YANG if self.is_yang_dun else EIGHT_SPIRITS_YIN
        fo = YANG_FLY_ORDER if self.is_yang_dun else YIN_FLY_ORDER
        si = next((i for i,p in enumerate(fo) if p==self.zhifu_palace), 0)
        for i, s in enumerate(sp):
            fi = (si+i)%9 if self.is_yang_dun else (si-i)%9
            if fi<0: fi+=9
            p = fo[fi]
            if p in self.chart: self.chart[p]["shen"] = s

    def _geju_analysis(self):
        for pn, d in self.chart.items():
            dp, tp = d["dipan"], d["tianpan"]
            gl = []
            if dp and tp and len(dp)==1 and len(tp)==1:
                pair = sorted([dp,tp])
                for entry in GEJU_DB:
                    if entry[0] is None: continue
                    if sorted(entry[0]) == pair:
                        gl.append((entry[1], entry[2], entry[3]))
            # 特殊格局检测
            if tp == "丙" and d.get("men") == "生门":
                sn = d.get("shen","")
                if sn == "九天": gl.append(("神遁","大吉","如有神助，谋为皆利"))
                elif sn in ("九地","太阴"): gl.append(("云遁","吉","隐蔽行事，求谋有成"))
                else: gl.append(("天遁","大吉","隐遁求安，宜守不宜攻"))
            if tp == "乙" and d.get("men") == "生门":
                sn = d.get("shen","")
                if sn == "六合": gl.append(("地遁","大吉","避凶趋吉，宜安营扎寨"))
                elif pn == 4: gl.append(("风遁","吉","顺风而行，事半功倍"))
                elif pn in (1,6): gl.append(("龙遁","吉","宜涉水修造"))
            if tp == "丁" and d.get("men") == "生门":
                sn = d.get("shen","")
                if sn in ("九地",): gl.append(("鬼遁","吉/凶参半","宜侦探惑敌"))
            if d.get("men") == "开门" and tp == "乙" and pn == 8:
                gl.append(("虎遁","吉","宜设伏捕猎"))
            if tp in SAN_QI and d.get("shen") == "值符":
                gl.append(("三奇得使","吉","奇门并至，百事亨通"))
            if tp == "丁" and d.get("men") in ("开门","休门"):
                gl.append(("玉女守门","吉","宜婚嫁宴请隐私事"))
            if tp in SAN_QI and d.get("men") in ("开门","休门","生门"):
                gl.append(("奇仪相佐","吉","吉上加吉，诸事顺遂"))
            # 入墓检测
            if tp == "丁" and pn in (6,8): gl.append(("丁奇入墓","凶","才华难展，文书受阻"))
            if tp == "乙" and pn in (6,8): gl.append(("乙奇入墓","凶","暗昧不通，谋为不成"))
            if tp == "丙" and pn in (5,8): gl.append(("丙奇入墓","凶","灾祸忽至，破财失禄"))

            d["geju"] = gl
            d["geju_level"] = self._eval_gl(gl)

    def _eval_gl(self, gl):
        if not gl: return "平"
        levels = {"大凶":-3,"凶":-2,"凶/半凶":-1.5,"凶/吉参半":-0.5,
                  "平":0,"平/凶":-0.5,"平/吉":0.5,
                  "小吉":1,"吉":1.5,"半凶": -1,
                  "大吉":2}
        total = sum(levels.get(g[1],0) for g in gl)
        if total >= 2: return "大吉"
        if total >= 1: return "吉"
        if total >= 0: return "平"
        if total >= -1: return "凶"
        return "大凶"

    def get_kong_wang(self):
        """获取旬中空亡宫位"""
        if not self.xun_shou: return []
        branches = XUN_KONG_WANG.get(self.xun_shou, [])
        palaces = []
        for b in branches:
            for pn, d in self.chart.items():
                # 空亡根据地支与宫位对应关系判断
                pass
        # 简化：返回空亡地支
        return branches

    def to_dict(self):
        result = {
            "time_info": {
                "solar": f"{self.year}-{self.month:02d}-{self.day:02d} {self.hour:02d}:00",
                "ganzhi_year": self.ganzhi_year,
                "ganzhi_month": self.ganzhi_month,
                "ganzhi_day": self.ganzhi_day,
                "ganzhi_shichen": self.ganzhi_shichen,
            },
            "chart_info": {
                "ju_number": self.ju_number,
                "ju_name": f"{'阳遁' if self.is_yang_dun else '阴遁'}{self.ju_number}局",
                "yuan": self.yuan,
                "jieqi": self.current_jieqi,
                "xun_shou": self.xun_shou,
                "xun_yi": self.xun_yi,
                "zhifu_palace": self.zhifu_palace,
                "zhifu_palace_name": PALACES.get(self.zhifu_palace,{}).get("name",""),
                "zhimen_palace": self.zhimen_palace,
                "zhimen_palace_name": PALACES.get(self.zhimen_palace,{}).get("name",""),
                "kong_wang": self.get_kong_wang(),
            },
            "palaces": {},
        }
        for pn in range(1, 10):
            d = self.chart.get(pn, self._new_palace(pn))
            result["palaces"][str(pn)] = {
                "name": PALACES[pn]["name"],
                "direction": PALACES[pn]["direction"],
                "element": PALACES[pn]["element"],
                "dipan": d["dipan"],
                "tianpan": d["tianpan"],
                "men": d["men"],
                "star": d["star"],
                "shen": d["shen"],
                "geju": [{"name":g[0],"level":g[1],"desc":g[2]} for g in d["geju"]],
                "geju_level": d["geju_level"],
            }
        return result

    def to_text(self):
        """文本格式输出完整排盘"""
        lines = []
        lines.append("=" * 50)
        lines.append("  ⚔️  奇 门 遁 甲 排 盘 ⚔️")
        lines.append("=" * 50)
        lines.append("")
        
        # 时间信息
        lines.append(f"📅 公历：{self.year}年{self.month}月{self.day}日 {self.hour:02d}时")
        lines.append(f"📅 年干支：{self.ganzhi_year}")
        lines.append(f"📅 月干支：{self.ganzhi_month}")
        lines.append(f"📅 日干支：{self.ganzhi_day}")
        lines.append(f"📅 时干支：{self.ganzhi_shichen}")
        lines.append("")
        
        # 局信息
        yin_yang = "阳遁" if self.is_yang_dun else "阴遁"
        yuan_map = {"upper":"上元","middle":"中元","lower":"下元"}
        lines.append(f"🎯 {yin_yang}{self.ju_number}局 · {yuan_map.get(self.yuan,'')} · {self.current_jieqi}")
        lines.append(f"📌 旬首：{self.xun_shou}（隐{self.xun_yi}）")
        lines.append(f"🦅 值符落：{PALACES.get(self.zhifu_palace,{}).get('name','')}")
        lines.append(f"🚪 值使落：{PALACES.get(self.zhimen_palace,{}).get('name','')}")
        kw = self.get_kong_wang()
        if kw:
            lines.append(f"⭕ 空亡：{' '.join(kw)}")
        lines.append("")
        
        # 九宫盘
        lines.append("-" * 50)
        lines.append("  📋 九 宫 完 整 排 盘")
        lines.append("-" * 50)
        
        # 洛书排版（后天八卦方位）
        #     巽四  |  离九  |  坤二
        #     震三  |  中五  |  兑七
        #     艮八  |  坎一  |  乾六
        grid = {}
        for pn in range(1, 10):
            d = self.chart.get(pn, self._new_palace(pn))
            grid[pn] = d
        
        def fmt_cell(pn):
            d = grid.get(pn, self._new_palace(pn))
            name = PALACES[pn]["name"]
            dp = d["dipan"] or "-"
            tp = d["tianpan"] or "-"
            men = d["men"] or "-"
            star = d["star"] or "-"
            shen = d["shen"] or "-"
            gj = d["geju"]
            gj_str = "; ".join(g[0]+"("+g[1]+")" for g in gj) if gj else "—"
            return (
                f"【{name}】\n"
                f"  地:{dp} 天:{tp}\n"
                f"  门:{men} 星:{star}\n"
                f"  神:{shen}\n"
                f"  格:{gj_str}"
            )
        
        # 输出每个宫位
        for pn in [4, 9, 2, 3, 5, 7, 8, 1, 6]:
            lines.append("")
            lines.append(fmt_cell(pn))
        
        lines.append("")
        lines.append("-" * 50)
        
        # 格局汇总
        lines.append("  🔍 格 局 汇 总 与 分 析")
        lines.append("-" * 50)
        
        da_ji, ji, ping, xiong, da_xiong = [], [], [], [], []
        for pn in range(1, 10):
            d = self.chart.get(pn, self._new_palace(pn))
            for g in d["geju"]:
                pname = PALACES[pn]["name"]
                entry = f"  [{pname}] {g[0]}（{g[1]}）：{g[2]}"
                if g[1] == "大吉": da_ji.append(entry)
                elif g[1] == "吉" or g[1] == "小吉": ji.append(entry)
                elif g[1] in ("平","平/吉"): ping.append(entry)
                elif g[1] in ("凶","凶/半凶","凶/吉参半"): xiong.append(entry)
                elif g[1] == "大凶": da_xiong.append(entry)
        
        if da_ji:
            lines.append("\n✨ 大吉格：")
            lines.extend(da_ji)
        if ji:
            lines.append("\n🌟 吉格：")
            lines.extend(ji)
        if ping:
            lines.append("\n➖ 平格：")
            lines.extend(ping)
        if xiong:
            lines.append("\n⚠️ 凶格：")
            lines.extend(xiong)
        if da_xiong:
            lines.append("\n💀 大凶格：")
            lines.extend(da_xiong)
        
        # 总体评估
        lines.append("")
        lines.append("=" * 50)
        lines.append("  📊 总 体 评 估")
        lines.append("=" * 50)
        
        total_good = len(da_ji) + len(ji)
        total_bad = len(da_xiong) + len(xiong)
        
        if total_good > total_bad * 2:
            verdict = "🟢 **吉** — 此局吉格众多，所问之事多有助益，可积极进取"
        elif total_good > total_bad:
            verdict = "🟡 **中偏吉** — 吉凶参半但吉略胜，宜稳中求进"
        elif total_good == total_bad:
            verdict = "🟠 **平** — 吉凶相当，事宜静观其变，伺机而动"
        elif total_bad > total_good * 2:
            verdict = "🔴 **凶** — 凶格偏多，宜守不宜攻，谨言慎行"
        else:
            verdict = "🟠 **中偏凶** — 凶多于吉，务必谨慎，不可冒进"
        
        lines.append(verdict)
        lines.append("")
        
        # 破局建议
        lines.append("  💡 破 局 建 议")
        lines.append("-" * 50)
        advice = self._generate_advice()
        lines.extend(advice)
        
        lines.append("")
        lines.append("---")
        lines.append("⚠️ 仅供参考，命理玄学信则有不信则无，理性看待。")
        return "\n".join(lines)

    def _generate_advice(self):
        """根据盘面生成破局建议"""
        advice = []
        
        # 收集所有格局信息
        all_geju = []
        for pn in range(1, 10):
            d = self.chart.get(pn, self._new_palace(pn))
            all_geju.extend([(pn, g) for g in d["geju"]])
        
        has_da_xiong = any(g[1]=="大凶" for _,g in all_geju)
        has_xiong = any(g[1] in ("凶","凶/半凶") for _,g in all_geju)
        has_da_ji = any(g[1]=="大吉" for _,g in all_geju)
        has_sanqi = any(g[0] in ("三奇得使","奇仪相佐") for _,g in all_geju)
        
        # 检查关键位置
        zhifu_data = self.chart.get(self.zhifu_palace, {})
        zhimen_data = self.chart.get(self.zhimen_palace, {})
        
        if has_da_xiong:
            advice.append("🚨 **大局有凶，首要原则：守为宜，不宜主动出击**")
            advice.append("   • 暂缓重大决策，避免签约、投资、远行")
            advice.append("   • 宜静养、读书、内省、处理日常事务")
        
        if has_xiong and not has_da_xiong:
            advice.append("⚠️ **盘中藏凶，需谨慎应对**")
            advice.append("   • 重要事项宜择吉日再行")
            advice.append("   • 处事以和为贵，避免争讼")
        
        if has_da_ji or has_sanqi:
            advice.append("✅ **盘中带吉，可借力而行**")
            advice.append("   • 有贵人相助之象，可主动寻求帮助")
            advice.append("   • 利于洽谈、签约、求谋（若无大凶格冲克）")
        
        # 值符值使分析
        zf_nature = ""
        if self.zhifu_palace in self.chart:
            zd = self.chart[self.zhifu_palace]
            zg = zd.get("geju",[])
            if zg:
                best = max(zg, key=lambda g: {"大吉":3,"吉":2,"小吉":1,"平":0}.get(g[1],-1))
                zf_nature = best[1]
        
        if zf_nature in ("大吉","吉"):
            advice.append(f"🦅 **值符落{PALACES.get(self.zhifu_palace,{}).get('name','')}逢吉**")
            advice.append("   • 值符主导之事顺遂，可依此方向行动")
        elif zf_nature in ("凶","大凶"):
            advice.append(f"🦅 **值符落宫见凶，宜避开此方向**")
        
        # 八门提示
        good_men = set(); bad_men = set()
        for pn in range(1, 10):
            d = self.chart.get(pn, self._new_palace(pn))
            men = d.get("men","")
            if men in ("开门","休门","生门"): good_men.add(men)
            elif men in ("死门","惊门","伤门"): bad_men.add(men)
        
        if good_men:
            advice.append(f"🚪 **吉门现：{'、'.join(good_men)}** — 可往吉门方向谋求")
        if bad_men:
            advice.append(f"🚪 **凶门现：{'、'.join(bad_men)}** — 避免此方向行事")
        
        # 三奇状态
        sanqi_status = {}
        for pn in range(1, 10):
            d = self.chart.get(pn, self._new_palace(pn))
            tp = d.get("tianpan","")
            if tp in SAN_QI:
                status = "✅" if not any("入墓" in g[0] for g in d.get("geju",[])) else "⚠️入墓"
                sanqi_status[tp] = (PALACES[pn]["name"], status)
        
        if sanqi_status:
            parts = [f"{k}({v[0]}{v[1]})" for k,v in sanqi_status.items()]
            advice.append(f"☯️ **三奇分布：{' / '.join(parts)}**")
        
        # 通用建议
        advice.append("")
        advice.append("📌 **通用策略：**")
        advice.append("   1. 吉多凶少 → 积极进取，把握时机")
        advice.append("   2. 吉凶相当 → 稳健行事，不冒风险")
        advice.append("   3. 凶多吉少 → 固守本位，以静制动")
        advice.append("   4. 若问具体事务 → 看相关用神所在宫位的吉凶")
        
        return advice


def main():
    import argparse
    parser = argparse.ArgumentParser(description="奇门遁甲排盘解卦系统")
    parser.add_argument("-q", "--question", default="", help="求测问题")
    parser.add_argument("-y", "--year", type=int, default=None, help="年")
    parser.add_argument("-m", "--month", type=int, default=None, help="月")
    parser.add_argument("-d", "--day", type=int, default=None, help="日")
    parser.add_argument("-H", "--hour", type=int, default=None, help="时（0-23）")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    args = parser.parse_args()
    
    now = datetime.now()
    year = args.year or now.year
    month = args.month or now.month
    day = args.day or now.day
    hour = args.hour if args.hour is not None else now.hour
    
    chart = QimenChart(year, month, day, hour, args.question)
    
    if args.json:
        print(json.dumps(chart.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(chart.to_text())


if __name__ == "__main__":
    main()
