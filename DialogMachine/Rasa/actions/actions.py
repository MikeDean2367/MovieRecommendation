# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import time
from typing import Any, Text, Dict, List, Union

import macropodus
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset
import hanlp
import numpy as np
import py2neo


class config:
    FILE_CONTRY_PATH = 'D:/Desktop/课程/创新实践/RecommendationProject/rasa/DB/country.txt'
    FILE_GENRE_PATH = 'D:/Desktop/课程/创新实践/RecommendationProject/rasa/DB/genre.txt'
    FILE_PERSONNAME_PATH = 'D:/Desktop/课程/创新实践/RecommendationProject/rasa/DB/personName.txt'
    YEAR_NOW = 2021  # 当前年份
    YEAR_RANGES_REDUCE = 5  # 之前的前几年
    YEAR_RANGES_ADD = 5  # 之后的后几年
    YEAR_RANGES_EQUAL = 1  # 左右波动一年
    YEAR_RANGES_AFTER = ["初", "末", "以后", "之后", "末", "以后"]
    YEAR_RANGES_BEFORE = ["之前", "以前"]
    YEAR_RANGES_NOW = ["左右", "前后"]
    YEAR_CENTURY = {"上个世纪": 1900, "上世纪": 1900, "上一个世纪": 1900, "二十世纪": 1900,
                    "本世纪": 2000, "二十一世纪": 2000, "这个世纪": 2000, "这一个世纪": 2000}
    YEAR_S_ONE = {"十": 10, "二十": 20, "三十": 30, "四十": 40, "五十": 50, "六十": 60, "七十": 70, "八十": 80, "九十": 90}
    YEAR_S_TWO = {"一二十": 10, "二三十": 20, "三四十": 30, "四五十": 40, "五六十": 50, "六七十": 60, "七八十": 70, "八九十": 80}
    YEAR = {"零": 0, "千": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
            "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9}

    TIME_RANGES_ADD_AND_REDUCE = 20
    TIME_2to1_2 = {  # 类似一两个小时 两三个小时 三四个小时 一二十分钟 七八十分钟
        "一两": 1, "一俩": 1, "一二": 1, "二三": 2, "两三": 2, "俩三": 2,
        "三四": 3, "四五": 4, "五六": 5, "六七": 6, "七八": 7, "八九": 8,

        "一二十": 10, "二三十": 20, "三四十": 30, "四五十": 40,
        "五六十": 50, "六七十": 60, "七八十": 70, "八九十": 80,
    }
    TIME_2to1_1 = {
        "一个半": 1.5, "二个半": 2.5, "俩个半": 2.5, "两个半": 2.5,
        "三个半": 3.5, "四个半": 4.5, "五个半": 5.5, "六个半": 6.5,
        "七个半": 7.5, "八个半": 8.5, "九个半": 9.5,
        "1个半": 1.5, "2个半": 2.5,
        "3个半": 3.5, "4个半": 4.5, "5个半": 5.5, "6个半": 6.5,
        "7个半": 7.5, "8个半": 8.5, "9个半": 9.5,
    }
    TIME_UNIT_HOUR = ["小时", "时"]
    TIME_UNIT_MINUTE = ["分钟", "分"]
    TIME_RANGES_BIGGER = [
        '超过',
        '不低于',
        '不得低于',
        '不少于',
        '不得少于',
        '不能少于',
        '不能够少于',
        '不可以少于',
        '不能低于',
        '不可以低于',
        '不能够低于',
        '以上',
        '大于',
        '大',
        '不短于',
        '不能短于',
        '不可短于',
        '不可以短于',
        '长',
        '长于',
    ]
    TIME_RANGES_LOWER = [
        '不到',
        '以内',
        '之内',
        '不能超过',
        '不得超过',
        '不超过',
        '不可以超过',
        '小于',
        '小',
        '少',
        '少于',
        '短',
        '短于',
        '不长于'
        '不得长于'
        '不能长于'
    ]
    TIME_RANGES_EQUAL = ["左右", "之间", "到"]

    SCORE_RANK = [  # 实体提取出来的是名次
        "名",
        "前",
        "名次",
        "排名",
        "第",
        "评分最高",
        "评分最好",
        "最好",
        "最高"
    ]
    SCORE_SCORE = [  # 实体提取出来的是豆瓣评分
        "评分",
        "分",
        ".",
    ]
    SCORE_SCORE_BIGGER = TIME_RANGES_BIGGER
    SCORE_SCORE_LOWER = TIME_RANGES_LOWER
    SCORE_SCORE_EQUAL = [
        "为", "等于"
    ]

    def __init__(self):
        pass


class query():
    def __init__(self):
        pass


class convert():

    def __init__(self, value: Text):
        self.HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)  # 世界最大中文语料库
        self.value = value

    def scoreRange(self):
        lens = 0
        flag = 0
        t = ""
        for text in config.SCORE_SCORE_BIGGER:
            if text in self.value:
                if len(text) > lens:
                    lens = len(text)
                    flag = 1
                    t = text
        for text in config.SCORE_SCORE_LOWER:
            if text in self.value:
                if len(text) > lens:
                    lens = len(text)
                    flag = 2
                    t = text
        for text in config.SCORE_SCORE_EQUAL:
            if text in self.value:
                if len(text) > lens:
                    lens = len(text)
                    flag = 3
                    t = text
        return flag

    def timeRange(self):
        '''
        时间范围判断
        :return:
        '''
        lens = 0
        flag = 0
        t = ""
        for text in config.TIME_RANGES_BIGGER:
            if text in self.value:
                if len(text) > lens:
                    lens = len(text)
                    flag = 1
                    t = text
        for text in config.TIME_RANGES_LOWER:
            if text in self.value:
                if text == "小":
                    if self.value.replace("小时", "").find("小") == -1:
                        continue
                if len(text) > lens:
                    lens = len(text)
                    flag = 2
                    t = text
        for text in config.TIME_RANGES_EQUAL:
            if text in self.value:
                if len(text) > lens:
                    lens = len(text)
                    flag = 3
                    t = text
        return flag

    def scoreConvert(self):
        ans = {
            "role": None,  # role == score 表示搜索评分，role == rank 表示搜索排名
            "value": None,  # 具体的值
            "count": None,  # 查询个数 如果为1表示只搜索一个
            "flag": None  # 用于role，为score才开
        }
        if self.value==None:
            return ans
        js = self.HanLP([self.value])
        tokens = js['tok/fine'][0]  # 分词结果
        properties = js['pos/pku'][0]  # 词性
        num = None
        for i in range(len(properties)):
            if properties[i] == 'm':
                try:
                    if tokens[i].find("第") != -1:
                        num = macropodus.chi2num(tokens[i].split("第")[1])
                    else:
                        num = macropodus.chi2num(tokens[i])
                    break
                except:
                    num = None
        flag_rank = False
        flag_score = False
        flag = 0  # 如果是分数的话，那么就要大于、小于、等于
        if num != None:
            # 有数字
            ans['value'] = num
            for x in config.SCORE_RANK:
                if x in self.value:
                    flag_rank = True
                    break

            for x in config.SCORE_SCORE:
                if flag_rank == True:
                    break
                if x in self.value:
                    flag_score = True
                    break

            if flag_score and flag_rank:
                print("error ! both flag being true is not allowed!")
            elif flag_score == True:
                flag = self.scoreRange()
                ans['flag'] = flag
                ans['role'] = 'score'
            elif flag_rank == True:
                ans['role'] = 'rank'
                if "第" in self.value:
                    ans['count'] = 1
                elif "前" in self.value:
                    ans['count'] = num
        else:
            # 没有数字
            if "最" in self.value:
                ans['role'] = 'rank'
                ans['value'] = 1
                ans['count'] = 1
            else:
                key = ["好","较","不错","超"]
                for k in key:
                    if k in self.value:
                        ans['role'] = 'rank'
                        ans['value'] = 10
                        ans['count'] = 10
        return ans

    def yearConvert(self):
        '''
        暂不支持如 八十年之前
        :return:
        '''
        if self.value==None:
            return 0,0
        if self.value.find("今年") != -1:
            return config.YEAR_NOW, config.YEAR_NOW
        elif self.value.find("去年") != -1:
            return config.YEAR_NOW - 1, config.YEAR_NOW - 1
        elif self.value.find("前年") != -1:
            return config.YEAR_NOW - 2, config.YEAR_NOW - 2
        self.value = self.value.replace("的", "")  # 去除语气词
        century = False if self.value.find("世纪") == -1 else True  # 世纪
        s = False if self.value.find("年代") == -1 else True  # 年代
        ranges = False  # 范围
        ranges_list = []  # 范围类型
        for x in config.YEAR_RANGES_BEFORE:
            if self.value.find(x) != -1:
                ranges = True
                ranges_list.append(0)
        for x in config.YEAR_RANGES_AFTER:
            if self.value.find(x) != -1:
                ranges = True
                ranges_list.append(1)
        for x in config.YEAR_RANGES_NOW:
            if self.value.find(x) != -1:
                ranges = True
                ranges_list.append(2)
        year_start = 0
        year_end = 0
        yearRange = 0
        if s == False and century == False:
            # 肯定就是年 2013/2013年/13年/一三年/二零一三年/两千零三年/九六年/九八年
            value = self.value.split("年")[0]
            if len(value) == 2:  # 肯定是一三/九六/九八类型的
                try:
                    # print(value)
                    if value[0] in ["零", "0", "1", "一", "2", "二"]:
                        year_start = 2000 + config.YEAR[value[0]] * 10 + config.YEAR[value[1]]
                        year_end = year_start
                    else:
                        year_start = 1900 + config.YEAR[value[0]] * 10 + config.YEAR[value[1]]
                        year_end = year_start
                except:
                    print("year error")
            elif len(value) == 4:
                year_start = config.YEAR[value[0]] * 1000 + config.YEAR[value[1]] * 100 + config.YEAR[value[2]] * 10 + \
                             config.YEAR[value[3]]
                year_end = year_start
            else:
                print("year 长度错误")
        elif s == False and century == True:
            # 只有世纪
            try:
                year_start = year_end = config.YEAR_CENTURY[self.value]
            except:
                print("century error")
        elif s == True and century == False:
            # 只有时代
            value = self.value.split("年代")[0]
            try:
                year_start = year_end = 1900 + config.YEAR_S_ONE[value]
            except:
                try:
                    year_start = 1900 + config.YEAR_S_TWO[value]
                    year_end = year_start + 10
                except:
                    print("years error")
        else:
            # 世纪和时代都有 上个世纪七八十年代 上世纪五十年代
            # 默认是先世纪后年代
            value_c = self.value.split("世纪")[0] + "世纪"
            value_s = self.value.split("世纪")[1].split("年代")[0]
            try:
                year_start = year_end = config.YEAR_CENTURY[value_c] + config.YEAR_S_ONE[value_s]
            except:
                try:
                    year_start = config.YEAR_CENTURY[value_c] + config.YEAR_S_TWO[value_s]
                    year_end = year_start + 10
                except:
                    print("years and century error")
        # 时间匹配完成，接下来匹配范围
        if ranges == True:
            if len(ranges_list) != 1:
                print("year range error")
            else:
                if ranges_list[0] == 0:
                    year_start -= config.YEAR_RANGES_REDUCE
                elif ranges_list[0] == 1:
                    year_end += config.YEAR_RANGES_ADD
                else:
                    year_start -= config.YEAR_RANGES_EQUAL
                    year_end += config.YEAR_RANGES_EQUAL
        return year_start, year_end

    def timeConvert(self):
        '''
        暂不支持2点5这样的输入
        :return:
        '''
        if self.value==None:
            return 0,0
        value = self.value
        js = self.HanLP([value])
        tokens = js['tok/fine'][0]  # 分词结果
        properties = js['pos/pku'][0]  # 词性
        flag = self.timeRange()  # 范围
        time_start = time_end = 0  # 最终结果
        if properties.count('m') == 1:
            # 只有一个数字
            for i in range(len(properties)):
                if properties[i] == 'm':
                    try:
                        time_start = time_end = config.TIME_2to1_1[tokens[i]]
                    except:
                        try:
                            time_start = config.TIME_2to1_2[tokens[i]]
                            if time_start <= 9:
                                time_end = time_start + 1
                            else:
                                time_end = time_start + 10
                        except:
                            try:
                                time_start = time_end = macropodus.chi2num(tokens[i])
                            except:
                                if tokens[i] == '半':
                                    time_start = time_end = 0.5
                                else:
                                    print("time and count(m)=1 error!")
                    finally:
                        break
        else:
            f = False
            i = 0
            while i + 2 < len(properties):
                if properties[i] == 'm' and properties[i + 1] == 'm':
                    # [一，两，个小时]
                    time_start = config.TIME_2to1_2[tokens[i] + tokens[i + 1]]
                    if time_start <= 9:
                        time_end = time_start + 1
                    else:
                        time_end = time_start + 10
                    break
                elif properties[i] == 'm' and properties[i + 1] != 'm' and properties[i + 2] == 'm':
                    tok = tokens[i] + tokens[i + 1] + tokens[i + 2]
                    if tok not in list(config.TIME_2to1_2.keys()) and tok not in list(config.TIME_2to1_1.keys()):
                        if tokens[i + 1] == "到":
                            # 真的有两个数字
                            time_start = macropodus.chi2num(tokens[i])
                            time_end = macropodus.chi2num(tokens[i + 2])
                        else:
                            time_start = time_end = macropodus.chi2num(tokens[i])
                        break
                    else:
                        # 出现 [两,个,半]这样
                        if f == False:
                            if tok in list(config.TIME_2to1_2.keys()):
                                time_start = time_end = config.TIME_2to1_2[tok]
                            else:
                                time_start = time_end = config.TIME_2to1_1[tok]
                            f = True
                        else:
                            if tok in list(config.TIME_2to1_2.keys()):
                                time_end = config.TIME_2to1_2[tok]
                            else:
                                time_end = config.TIME_2to1_1[tok]
                            break
                        i += 3
                elif properties[i] == 'm' and properties[i + 1] != 'm' and properties[i + 2] != 'm':
                    tok = tokens[i]
                    # 出现 [两,个,半]这样
                    if f == False:
                        if tok in list(config.TIME_2to1_2.keys()):
                            time_start = time_end = config.TIME_2to1_2[tok]
                        elif tok in list(config.TIME_2to1_1.keys()):
                            time_start = time_end = config.TIME_2to1_1[tok]
                        else:
                            time_start = time_end = macropodus.chi2num(tok)
                        f = True
                    else:
                        if tok in list(config.TIME_2to1_2.keys()):
                            time_end = config.TIME_2to1_2[tok]
                        elif tok in list(config.TIME_2to1_1.keys()):
                            time_end = config.TIME_2to1_1[tok]
                        else:
                            time_end = macropodus.chi2num(tok)
                        break
                    i += 3
                else:
                    i += 1
        # 确定单位
        unit_h = unit_m = -1
        for i in config.TIME_UNIT_HOUR:
            if i in value:
                unit_h = value.find(i)
        for i in config.TIME_UNIT_MINUTE:
            if i in value:
                unit_m = value.find(i)
        if unit_h == -1 and unit_m == -1:
            if time_start < 30:
                time_start *= 60
            if time_end < 30:
                time_end *= 60
        elif unit_h == -1 and unit_m != -1:
            pass
        elif unit_h != -1 and unit_m == -1:
            time_start *= 60
            time_end *= 60
        elif unit_h < unit_m:
            time_start *= 60
        elif unit_m < unit_h:
            time_end *= 60

        # 范围控制
        if time_start == time_end:
            if flag == 1:
                time_end = 1e5
            elif flag == 2:
                time_start = 0
            elif flag == 3:
                time_end += config.TIME_RANGES_ADD_AND_REDUCE
                time_start -= config.TIME_RANGES_ADD_AND_REDUCE
        return time_start, time_end


'''
你想看什么类型的电影呢
由哪个国家制作的呢
对于演员或者编剧有什么要求吗
时长有没有要求
'''


class ValidateMoviesForm(FormValidationAction):

    def __init__(self):
        self.list_personName = []
        self.list_country = []
        self.list_genre = []
        print("[%s] aciton.py: 正在加载数据库，请稍后" % str(time.ctime()))
        with open(config.FILE_GENRE_PATH, "r", encoding="utf-8", errors="ignore") as f:
            l = f.readlines()
            for i in range(len(l)):
                l[i] = l[i].replace("\n", "").strip()
        self.list_genre = l

        with open(config.FILE_CONTRY_PATH, "r", encoding="utf-8", errors="ignore") as f:
            l = f.readlines()
            for i in range(len(l)):
                l[i] = l[i].replace("\n", "").strip()
        self.list_country = l

        with open(config.FILE_PERSONNAME_PATH, "r", encoding="utf-8", errors="ignore") as f:
            l = f.readlines()
            for i in range(len(l)):
                l[i] = l[i].replace("\n", "").strip()
        self.list_personName = l

        self.list_genre.append("无")
        self.list_country.append("无")
        self.list_personName.append("无")
        print(self.list_country)
        print(self.list_genre)
        print("[%s] aciton.py: 加载完毕" % str(time.ctime()))

    def name(self) -> Text:
        return "validate_movies_form"

    def genre_db(self) -> List[Text]:
        # return ["无","悬疑","古装","爱情","动作"]
        return self.list_genre

    def country_db(self) -> List[Text]:
        # return ["无","中国","大陆","美国"]
        return self.list_country

    def personName_db(self) -> List[Text]:
        # return ["无", "周星驰", "周润发", "朱亚文", "吴京"]
        return self.list_personName

    def validate_genre(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("genre: %s" % slot_value)
        print("test!!!!!")
        if slot_value not in self.genre_db():
            dispatcher.utter_message(text="对不起，我没有听懂您的意思呢~对于电影类型有悬疑、喜剧、动作、爱情、战争等类型哦")
            return {"genre": None}
        else:
            return {"genre": slot_value}

    def validate_country(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("country: %s" % slot_value)
        print(self.list_country)
        if slot_value not in self.country_db():
            dispatcher.utter_message(text="对不起啦，我又不能懂你在说什么哦~关于国家的话请输入中文国家哦~")
            return {"country": None}
        else:
            return {"country": slot_value}

    def validate_personName(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("personName: %s" % slot_value)
        if slot_value not in self.personName_db():
            dispatcher.utter_message(text="对不起，我有没有听懂您的意思哈~我也在不断的改进。关于导演或者演员你只要说出他们的名字即可哦~比如影颖我就比较喜欢看周星驰的电影哦")
            return {"personName": None}
        else:
            return {"personName": slot_value}

    def validate_time(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("time: %s" % slot_value)
        isError = False
        if slot_value == "无":
            return {"time": slot_value}
        for value in slot_value:
            cvt = convert(value)
            try:
                time_start, time_end = cvt.timeConvert()
                if time_start >= 0 and time_start <= time_end:
                    isError = False
                else:
                    isError = True

            except:
                isError = True

            if isError == True:
                dispatcher.utter_message(text="请输入正确的时长哦（如100分钟左右，一两个小时等）~")
                return {"time": None}
            else:
                return {"time": slot_value}
        return {"time": None}


# class MovieForm(FormAction):
#     '''
#     每一次form action被调用的时候，它将向用户询问required_slots中还没有被赋值的下一个slot。
#     这个行为的执行是通过寻找叫做utter_ask_{slot_name}的模板实现的，因此你可以在domain文件中针对需要的slot给出模板定义。
#     '''
#     def name(self) -> Text:
#         return "Movie_Form"
#
#     @staticmethod
#     def required_slots(tracker: "Tracker") -> List[Text]:
#         # 需要的槽位信息
#         return ['time','genre','']
#
#     def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
#         # "槽位名称":[self.from_entity(),self.from_intent()]
#         # 槽位填充规则
#         return {}
#
#     def submit(
#         self,
#         dispatcher: "CollectingDispatcher",
#         tracker: "Tracker",
#         domain: "DomainDict",
#     ) -> List[Dict]:
#         # 所有槽位填充完毕后需要做的事情
#         # [SlotSet()]
#         return []


#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


class MoviesQueryAction(Action):
    # 普通意图触发后完成的动作
    def name(self) -> Text:
        return "action_movies_query"

    def run(
            self,
            dispatcher: "CollectingDispatcher",
            tracker: Tracker,
            domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        value_genre, value_country, value_movieName, value_personName, value_time, value_score, value_year, value_movieName = \
            tracker.get_slot('genre'), tracker.get_slot('country'), tracker.get_slot('movieName') , tracker.get_slot('personName'), \
            tracker.get_slot('time'), tracker.get_slot('score'), tracker.get_slot('year'), tracker.get_slot('movieName')
        # dispatcher.utter_message(text="你好")
        # return []
        print(value_genre)
        print(value_country)
        print(value_personName)
        message = {
            "genre": value_genre,
            "country": value_country,
            "movieName": value_movieName,
            "personName": value_personName,
            "time": convert(value_time).timeConvert(),
            "score": convert(value_score).scoreConvert(),
            "year": convert(value_year).yearConvert()
        }
        dispatcher.utter_message(text=str(message))
        return [AllSlotsReset()]


class MoviesFormSubmitAction(Action):
    # 表单填充完成后触发的事件
    def name(self) -> Text:
        return "action_movies_form_submit"

    async def run(
            self,
            dispatcher: "CollectingDispatcher",
            tracker: Tracker,
            domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        value_genre, value_country, value_personName, value_time = \
            tracker.get_slot('genre'), tracker.get_slot('country'), tracker.get_slot('personName'), tracker.get_slot(
                'time')
        jsons = {
            "genre": None,
            "country": None,
            "movieName": None,
            "personName": None,
            "time": (0,0),
            'score': {
                'role': None, 'value': None, 'count': None, 'flag': None
            },
            "year": (0, 0)
        }
        message = "正在查询"
        if value_genre != "无":
            message += "类型为" + value_genre + "、"
            jsons['genre'] = value_genre
        if value_country != "无":
            message += "在" + value_country + "发行、"
            jsons['country'] = value_country
        if value_personName != "无":
            message += "由" + value_personName + "等人参与、"
            jsons['personName'] = value_personName
        if value_time != "无":
            cvt = convert(value_time)
            time_start, time_end = cvt.timeConvert()
            message += "时长在" + str(time_start) + "~" + str(time_end) + "分钟、"
            jsons['time'] = (time_start, time_end)
        # dispatcher.utter_message(text=message[0:-1] + "的电影")
        dispatcher.utter_message(text=str(jsons))
        return [AllSlotsReset()]


if __name__ == '__main__':
    text = ["一小时以内"]
    # text = [
    #     '两三个小时以内',
    #     '100分钟左右',
    #     '100分钟以上',
    #     '不超过两个小时',
    #     '不少于两个小时',
    #     '100到200分钟内',
    #     '一个小时到两个小时以内',
    #     '一两个小时以内',
    #     '一两个小时左右',
    #     '1个小时到2个小时之间',
    #     '九十分钟以内/之内',
    #     '209分钟上下',
    #     '一百到一百五十分钟之间',
    #     '103到104之间',
    #     '两个小时不到',
    #     '不能低于一个半小时',
    #     '俩小时以内',
    #     '2.5小时以内',
    #     '2.5个小时以内',
    #     '不低于一个小时',
    #     '不到两个小时',
    #     '七八十分钟',
    #     '一到两三个小时',  # (60.0, 1380.0) 数据问题
    #     '半个小时',  # (0, 30.0)
    #     '一个半到两个半小时',
    #     "一个半到俩个半小时",
    #     "一个小时到两个小时以内",
    # ]
    # text = [
    #     '评分前十',
    #     '评分大于九',
    #     '分数大于9分',
    #     '5.9分以上',
    #     '评分第一',
    #     '评分很高',
    #     '高分',
    #     '评分最好的十三部',
    #
    # ]
    for i in text:
        A = convert(i)
        print(A.timeConvert())
    # A = convert("半个小时")
    # print(A.timeConvert())