'''
求解相似度的时间瓶颈在IO，尝试用fread,据说会很快
推荐算法
map(function,iterable) 对iterable的每个元素作用function并返回iterable map(square, [1,2,3,4,5])   # 计算列表各个元素的平方
filter(function,iterable) 对iterable的每个元素作用function看看是否为true，为true则保留 tmplist = filter(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
'''
import pandas as pd
import time
from typing import Dict, AnyStr,List
from langconv import *
from string import punctuation
import numpy as np
from py2neo import Graph, Node, Relationship, Subgraph
import os
from math import pow

def preProcessCountry(country):
    # 将传入的国家规范化
    # 删除英文 空格 标点
    # 转换成简体
    # 此处的变量名称为country是为了代码理解，但是香港、台湾、澳门始终是中国不可分割的领土
    # 坚持一个中国原则！
    add_punc = punctuation + '0123456789 '
    ans = []
    for i in country:
        if (i not in add_punc) and (i >= 'a' and i <= 'z') == False and (i >= 'A' and i <= 'Z') == False:
            ans.append(i)
    country = Converter('zh-hans').convert("".join(ans))
    if "香港" in country:
        return "香港"
    elif "台湾" in country:
        return "台湾"
    elif "中国" in country:
        return "大陆"
    return country

class Config:
    def __init__(self):
        self.file_path_country_genre = r"../../init.txt"  # 第一行为类型 第二行为国家
        # 第一个参数为召回个数 第二个参数为向量，第三个参数可选，默认为余弦，可以指定为distance
        self.file_path_calsimilarity = r"C:\Users\MikeDean\source\repos\Project1\x64\Debug\Project1.exe"  # 计算相似度
        self.file_path_relationships_csv = r"relationships.csv"  # 用于映射自定id与豆瓣id
        self.file_path_moviesInformation_csv = r"moviesInformation.csv"
        self.file_path_moviesVector_txt = r"D:/Desktop/movies_vector.txt"   # 每部电影的特征向量，每一行为一个电影的向量，电影的行号即为id（从0开始，需要转换

        self.num_recall = 500   # 电影召回数量
        self.num_standard_deviation_critical_value = 1  # 标准偏差临界值 大于这个临界值即为不稳定
        self.num_penalty_rating = 1     # 在更新用户向量的时候用到，features+num_penalty_rating*feature 越低说明新的电影影响更小
        self.num_vector_dim = 32        # 当前特征向量的维度

        self.num_group_duration_upper = 120 # >120为一组
        self.num_group_duration_lower = 60  # <120 && >60
        self.num_group_rating_upper = 8.5   # 豆瓣评分
        self.num_group_rating_lower = 7.5
        self.num_group_year_upper = 2019
        self.num_group_year_lower = 2000    # 年

class User:
    def __init__(self, userId: AnyStr , feature: AnyStr, movies: Dict, time_:List):
        self._config = Config()  # 参数
        self.userId = userId  # 用户的唯一认证id
        self._feature = feature.replace(" ", "").strip()  # 用户的特征向量，用逗号分割 如 "1,2,3,4,5,6,7,8,9,10,1,2,3,4,5,6,7..."
        self._movies = movies  # 存储的是看过的电影id, 为一个键值对, 为 电影id:评分 {1123:9.5,2234:10.0}
        self._time = time_  # 与_movies对应，置为看过的日期                    [0,       0,       ]
        self._country = None  # 用户的国家喜好  # 就按照国家来统计
        self._duration = None  # 用户的时长偏好  # 分为三类 一小时以内/1~2小时/2小时以上
        self._genre = None  # 用户的电影类别喜好    # 直接开数组
        self._year = None  # 用户的电影上映日期喜好  # 2000年以前/2000~2019/2020~
        self._rating = None  # 评分   # 分组 <7.5 7.5~8.5 >8.5
        self._movieInfo = None  # 电影信息 为dict, {豆瓣id: [上映年份,评分,类别,国家,时长]}
        self._movieInfo_dicts = {
            'year':0, 'rating':1, 'genre':2, 'country':3, 'duration':4
        }   # movieInfo values中的顺序
        self._movieVectors = None   # 每个电影的特征向量，为一个字典类型     {0:[1.1,2.2,3.3,...]} 都为数字
        self._initializeParameter()  # 初始化各个参数

    def _removeMovieYouHaveSeen(self,movieId:List)->List:
        '''
        移除你看过的电影
        :param movieId: 豆瓣电影list
        :return: 豆瓣电影list
        '''
        for haveSeenId in self._movies:
            if haveSeenId in movieId:
                movieId.remove(haveSeenId)
        return movieId

    def _convertMovieId2MyId(self, movieIdList):
        '''
        将豆瓣电影id转换成以3为开始的我的id
        :param movieIdList:
        :return:
        '''
        data = pd.read_csv(self._config.file_path_relationships_csv)
        movieId = {}
        movieIdx = 3
        personId = {}
        personIdx = 31444
        new = pd.DataFrame(np.empty(data.shape), columns=['movie_id', 'person_id', 'role'], dtype=int)
        role = {'author': 1, 'actor': 0, 'director': 2}
        cnt = 0
        for row in data.itertuples():
            filmId = getattr(row, 'movie_id')
            pId = getattr(row, 'person_id')
            relationName = getattr(row, 'role')
            if filmId not in movieId:
                movieId[filmId] = movieIdx
                movieIdx += 1
            if pId not in personId:
                personId[pId] = personIdx
                personIdx += 1
            # new.loc[cnt]=[movieId[filmId],personId[pId],role[relationName]]
            cnt += 1
        ans = []
        for id in movieIdList:
            ans.append(movieId[id])
        return ans

    def _convertMyId2MovieId(self, myIdList):
        '''
        输入为c++cuda得到的id，需要将其转换为豆瓣id
        :param myIdList: c++cuda得到的电影id，即从0开始
        :return: 豆瓣id
        '''

        def getIdMap():
            '''
            获取MovieId和Index的对应关系
            :return: 格式为{Index:MovieId,}
            '''
            data = pd.read_csv(self._config.file_path_relationships_csv)
            movieId = {}
            movieIdx = 3
            personId = {}
            personIdx = 31444
            for row in data.itertuples():
                filmId = getattr(row, 'movie_id')
                pId = getattr(row, 'person_id')
                if filmId not in movieId:
                    movieId[filmId] = movieIdx
                    movieIdx += 1
                if pId not in personId:
                    personId[pId] = personIdx
                    personIdx += 1
            movies_dicts = dict(zip(movieId.values(), movieId.keys()))
            actor_dicts = dict(zip(personId.values(), personId.keys()))
            return movies_dicts, actor_dicts

        movies_dict, actors_dict = getIdMap()  # 自己的索引(从3开始)：电影的索引
        ans = []
        for a in myIdList:
            ans.append(movies_dict[a + 3])  # 因为C++产生的id从0开始，因此要偏移一下
        return ans

    def _analyseBaseQuality(self):
        '''
        时长/上映日期/国家/类别/评分 标准差越大，说明越离散，也就越趋向于重要
        从众-分析用户偏好
        :return: 每个特征下的值和每个特征的权重
        features, values, weights_ 这三个都是字典，字典的格式如下
        {
            country: [], year: [], genre: [], rating: [], duration: []
        }
        features 已经排序，值为按照点击次数从大到小排列，如可能为["中国","美国","英国","印度","巴西"]
        values 与features对应，但是过滤掉为0的值，即values中值的个数小于等于features值的个数
        weight 已经排序，按照标准差降序排列，值为标准差
        '''

        def normalization(data):
            # 归一化
            _range = np.max(data) - np.min(data)
            return (data - np.min(data)) / _range

        def deal(var):
            # var = {"巴西":0, "中国":234, "美国":50, "印度":0, "英国":4}
            # 返回指标的名称或id（已排序），指标的非0次数，指标的标准差
            var = sorted(var.items(), key=lambda item: item[1])
            var.reverse()  # 按照量从大到小排序  [("中国":234),("美国":50),("英国",4),("印度":0),("巴西":0)]
            var_list = list(map(lambda x: x[0],var))  # ["中国","美国","英国","印度","巴西"]
            var_weights = list(filter(
                lambda x: x != 0, list(map(lambda x: x[1], var))  # 过滤掉为0的 [234,50,4]
            ))
            # 不用考虑量纲，因为所有的都是次数好像，单位都是一样的
            return var_list, var_weights, np.std(var_weights)

        features = {}
        values = {}
        weights = {}

        # 国家
        features['country'], values['country'], weights['country'] = deal(self._country)

        # 年份 list
        '''         id      counts
        <2000:      0       0
        <2019:      1       20   
        >2020:      2       8
        '''
        year = dict(enumerate(self._year, 0))
        features['year'], values['year'], weights['year'] = deal(year)

        # 类型 genre
        features['genre'], values['genre'], weights['genre'] = deal(self._genre)

        # 评分 rating
        rating = dict(enumerate(self._rating, 0))
        features['rating'], values['rating'], weights['rating'] = deal(rating)

        # 时长 duration
        duration = dict(enumerate(self._duration, 0))
        features['duration'], values['duration'], weights['duration'] = deal(duration)

        tmp = sorted(weights.items(), key=lambda item: item[1])
        tmp.reverse()
        weights_ = {}
        for t in tmp:
            weights_[t[0]] = t[1]
        return features, values, weights_

    def _connectNeo4j(self):
        print("[%s] 正在连接Neo4j" % time.ctime())
        test_graph = Graph(
            "http://localhost:7474",
            auth=("neo4j", "mikedean")
        )
        print("[%s] 连接Neo4j成功" % time.ctime())
        return test_graph

    def _initializeParameter(self):
        '''
        对国家/电影类别/时长/上映年份进行统计，同时对电影信息进行加载
        :return:
        '''

        # 获取电影信息，比如电影的评分、上映日期、时长、发行国家等
        data = pd.read_csv(
            self._config.file_path_moviesInformation_csv
        )
        dicts = {}
        for row in data.itertuples():
            dicts[int(getattr(row, 'id'))] = [
                getattr(row, 'year'), getattr(row, 'rating'), getattr(row, 'genre').strip().replace(" ",""),
                getattr(row, 'country').strip().replace(" ",""), getattr(row, 'duration')
            ]
        self._movieInfo = dicts

        # 加载每部电影的特征向量
        with open(self._config.file_path_moviesVector_txt,"r") as f:
            data = f.readlines()
        dicts = {}
        i = 0
        for d in data:
            lists = d.strip().split(',')
            dicts[i] = [float(l) for l in lists]
            i += 1
        self._movieVectors = dicts

        graph = self._connectNeo4j()  # 获取连接
        self._year = [0, 0, 0]  # 2000年以前/2000~2019/2020~
        self._duration = [0, 0, 0]  # 分为三类 一小时以内/1~2小时/2小时以上
        self._rating = [0, 0, 0]  # 分组 <7.5 7.5~8.5 >8.5
        self._genre = {}  # 电影类别
        self._country = {}  # 国家

        # 初始化电影类别和国家
        with open(self._config.file_path_country_genre, "r", encoding='utf-8', errors='ignore') as f:
            data = f.readlines()
        for i in data[0].strip().split('\t'):
            self._genre[i] = 0
        for i in data[1].strip().split('\t'):
            self._country[i] = 0

        # 开始统计
        movies_id = list(self._movies.keys())
        for id in movies_id:
        # for id in self._movies:
            node = graph.nodes.match('Movie', id=int(id)).first()  # 找到id
            print("node结果:", node)
            if node==None:
                self._movies.pop(id)
                continue
            # 统计时长
            duration = int(node['duration'])
            self._duration[
                0 if duration // self._config.num_group_duration_lower == 0 else 1 if duration // self._config.num_group_duration_upper == 0 else 2
            ] += 1
            # 统计评分
            rating = float(node['rating'])
            self._rating[0 if rating < self._config.num_group_rating_lower else 1 if rating < self._config.num_group_duration_upper else 2] += 1
            # 统计类型 Genre
            cursor = graph.run("MATCH (m:Movie {id:%d})--(c:Genre) RETURN c" % int(id))
            for record in cursor:
                tmp = str(record).replace("'", "").replace(")", "")
                self._genre[tmp[tmp.find('value=') + len("value="):]] += 1
            # 统计上映年份
            cursor = graph.run("MATCH (m:Movie {id:%d})--(c:Time) RETURN c" % int(id))
            for record in cursor:
                tmp = str(record).replace("'", "").replace(")", "")
                year = int(tmp[tmp.find('value=') + len("value="):])
                self._year[0 if year < self._config.num_group_year_lower else 1 if year < self._config.num_group_year_upper else 2] += 1
            # 统计国家
            cursor = graph.run("MATCH (m:Movie {id:%d})--(c:Country) RETURN c" % int(id))
            for record in cursor:
                tmp = str(record).replace("'", "").replace(")", "")
                tmp = preProcessCountry(tmp[tmp.find('value=') + len("value="):])
                if tmp in self._country:
                    self._country[tmp] += 1
                else:
                    print("[%s] 未识别的国家" % time.ctime())

        print("[%s] 统计成功" % time.ctime())

    def recommendBaseMovie(self, movieId:int, number=20)->List[int]:
        '''
        推荐和movieId相似的电影，评分大于7.5且类型相似的
        :param movieId: 电影id
        :param number: 推荐的电影个数，默认为20条
        :return:
        '''
        # 首先将movieId转换成myId，获取到该电影的向量后放入cuda跑，跑完后返回，然后又转换成movieId
        print("[%s] 查找电影id为%s的评分、类型和拍摄地区" % (time.ctime(), movieId))
        genre = self._movieInfo[movieId][self._movieInfo_dicts['genre']].strip().replace("/","|")
        country = self._movieInfo[movieId][self._movieInfo_dicts['country']].strip().split('/')
        print("[%s] 查找电影id为%s的特征向量" % (time.ctime(),movieId))
        myId = self._convertMovieId2MyId([movieId])[0]-3    # 减3的原因是要送到c++
        feature = ",".join([str(i) for i in self._movieVectors[myId]])        # 找到对应的特征向量
        recallNumber = self._config.num_recall  # 召回电影个数
        print("[%s] 正在执行相似度计算" % time.ctime())
        with os.popen("%s %d %s" % (self._config.file_path_calsimilarity, recallNumber, feature)) as f:
            tmp = f.readlines()
        myId = tmp[-1].replace(" ","").strip()[:-1].split(",")
        # myId = os.popen("%s %d %s" % (self._config.file_path_calsimilarity, recallNumber, feature))[-1].replace(
        #     " ", "").strip().split(',')
        print("[%s] 执行完毕" % time.ctime())
        myId = [int(id) for id in myId] # 从0开始
        movieId_recommend = self._convertMyId2MovieId(myId)  # 转换成功
        data = []
        movieId_recommend = self._removeMovieYouHaveSeen(movieId_recommend) # 移除看过的电影
        for id in movieId_recommend:
            tmp = self._movieInfo[id]
            tmp.extend([id])
            data.append(tmp)
        data = pd.DataFrame(data)
        country_ = ""
        for c in country:
            country_ += preProcessCountry(c)
        ans = data[
            ((data[self._movieInfo_dicts['genre']].str.contains(genre)) &
             (data[self._movieInfo_dicts['rating']]>=self._config.num_group_rating_lower) |
             (data[self._movieInfo_dicts['country']].str.contains(country_)))
        ].copy()
        print(ans)
        ans.sort_values(by=self._movieInfo_dicts['rating'],ascending=False,inplace=True)    # 按评分升序排列

        answer = [ans.iloc[i, len(self._movieInfo_dicts)] for i in range(number)]
        return answer

    def recommendMovies(self, number=50)->List[int]:
        '''
        根据用户向量推荐电影
        :param number: 推荐的电影个数，默认为50条
        :return: 电影id
        '''
        recallNumber = self._config.num_recall  # 召回电影
        print("[%s] 正在执行相似度计算" % time.ctime())
        # 此处的电影id从0开始计数，首先要将其+3映射到训练时的id，然后根据函数转换到豆瓣id
        with os.popen("%s %d %s" % (self._config.file_path_calsimilarity, recallNumber, self._feature)) as f:
            tmp = f.readlines()
        print("[%s] 召回成功，准备精排" % time.ctime())
        movieId = tmp[-1].replace(" ","").strip()[:-1].split(",")
        movieId = [int(id) for id in movieId]
        movieId = self._convertMyId2MovieId(movieId)  # 转换成功
        movieId = self._removeMovieYouHaveSeen(movieId) # 移除看过的电影
        # 召回电影信息填充
        data = []   # 电影的信息,通过self._movieInfo_dict去访问，如果想要知道国家在哪里，则只要movieInfo_dict['country']即可得到
        movieInfo_dicts = self._movieInfo_dicts.copy()

        movieInfo_dicts['country_'] = len(self._movieInfo_dicts)+1
        movieInfo_dicts['genre_'] = len(movieInfo_dicts)+1
        movieInfo_dicts['duration_'] = len(movieInfo_dicts)+1
        movieInfo_dicts['year_'] = len(movieInfo_dicts)+1
        movieInfo_dicts['rating_'] = len(movieInfo_dicts)+1

        for id in movieId:
            tmp = self._movieInfo[id]
            tmp.extend([id,0,0,0,0,0])
            data.append(tmp)   # 最后四个0是占位符
        data = pd.DataFrame(data)
        data[len(self._movieInfo_dicts)].astype("int")
        # 召回成功，接下来开始精排
        # 方差越大，说明特征越明显
        # 方差越小，则在所选类型中均匀分布
        features, values, weights = self._analyseBaseQuality()  # 具体参数说明看函数
        # print(features)
        # print(values)
        # print(weights)
        # 采用将都数值化然后进行排序，对于电影类型，有过观影历史的就赋予一个值，参考指数，该值需要满足 sum(x[0],x[1],...,x[N-1])<x[N] 只有指数可以满足

        # 数值化电影类型和国家 越大越好
        tmp = ['genre','country']
        for t in range(2):
            # 先判断一下稳不稳定,如果稳定，则对非0的设为1，如果不稳定，则按照指数权重相加
            isStable = False
            if weights[tmp[t]]<self._config.num_standard_deviation_critical_value:  # 稳定，则不进行排序，因为所有的都是一样的值
                isStable = True
            start = len(
                values[tmp[t]]
            )-1  # 对应于2^start
            # print(start)
            for i in range(
                    len(
                        values[tmp[t]])):   # 非0的个数
                for j in range(len(data)):  # 遍历
                    # 查找 赋值只有满足条件的才可以
                    weight = 0
                    types = data.loc[j,movieInfo_dicts[tmp[t]]].split('/')   # 获取当前电影的类型或者国家
                    if isStable:
                        weight = 1
                        for ty in types:
                            if ty in features[tmp[t]]:  # 只要这个电影的有一个命中，就置为1
                                data.loc[j,movieInfo_dicts[str(tmp[t]+'_')]] = weight
                                break
                    else:
                        for ty in types:
                            if tmp[t]=='country':
                                ty = preProcessCountry(ty)
                            if ty in features[tmp[t]]:    # 因为有的是英文的或者表述不规范的，因此需要事先判断一下
                                weight += int(pow(2,start-features[tmp[t]].index(ty)))
                                # print(int(pow(2,start-features[tmp[t]].index(ty))))
                        # print(weight,movieInfo_dicts[str(tmp[t]+'_')])
                        # print(tmp[t]+'_')
                        data.loc[j,movieInfo_dicts[str(tmp[t]+'_')]] = weight

        # 数值化电影时长、上映年份、评分
        # 同样的，需要先判断是否稳定
        tmp = ['duration','year','rating']
        for t in range(len(tmp)):
            isStable = False
            if weights[tmp[t]]<self._config.num_standard_deviation_critical_value:
                isStable = True
            start = len(values[tmp[t]])+1 # 当前非0的个数
            for i in range(len(
                values[tmp[t]]
            )):
                for j in range(len(data)):
                    idx, idx_ = movieInfo_dicts[tmp[t]], movieInfo_dicts[tmp[t]+'_']
                    if tmp[t]=='duration':
                        upper = self._config.num_group_duration_upper
                        lower = self._config.num_group_duration_lower
                    elif tmp[t]=='year':
                        upper = self._config.num_group_year_upper
                        lower = self._config.num_group_year_lower
                    else:
                        upper = self._config.num_group_rating_upper
                        lower = self._config.num_group_rating_lower
                    # 获取当前电影对应的档位
                    if data.loc[j,idx]<lower:
                        p = 0
                    elif data.loc[j,idx]<upper:
                        p = 1
                    else:
                        p = 2
                    if isStable:    # 稳定是对单击过的而言的
                        if p in features[tmp[t]][0:len(values[tmp[t]])]:
                            data.loc[j, idx_] = 1
                    else:
                        if p in features[tmp[t]][0:len(values[tmp[t]])]:
                            data.loc[j,idx_] = start - features[tmp[t]].index(p)

        # 到此为止，数值化基本完成，接下来就是对其按照方差进行排序
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.max_rows', None)
        sort_list = [movieInfo_dicts[l+'_'] for l in list(weights.keys())]
        # data.to_csv("test_or.csv",encoding='utf-8')
        data.sort_values(by = sort_list,ascending=[False,False,False,False,False],inplace=True)
        answer = [data.iloc[i,len(self._movieInfo_dicts)] for i in range(number)]
        # data.to_csv("test.csv",encoding='utf-8')
        return answer

    def seeMovie(self, movieId:int, score:float)->AnyStr:
        '''
        根据评分来更新用户的特征向量，同时更新对应的统计变量
        就直接相加即可
        :param movieId: 看过的电影id 豆瓣id
        :param score: 该电影的评分    0~10 之前吧
        :return:
        '''
        # self._feature + score/10*vector[movieId]
        myId = self._convertMovieId2MyId([movieId])[0]-3   # 因为这个函数就是以3开始的
        feature = self._movieVectors[myId]
        myFeature = [float(t) for t in self._feature.split(',')]
        newFeature = []
        for i in range(len(feature)):
            newFeature.append(myFeature[i]+score/10*feature[i]*self._config.num_penalty_rating)
        self._feature = ",".join(str(t) for t in newFeature)
        return self._feature

    def initialFeature(self):
        '''
        客户端传过来的是None，则需要根据他们的{电影id:评分}对其进行初始化
        :return: string
        '''
        feature = ""
        for i in range(self._config.num_vector_dim):
            feature += "0,"
        self._feature = feature[:-1]  # 去除最后一个逗号
        for id in self._movies:
            self.seeMovie(id,self._movies[id])
        return self._feature


    def parseMovie(self,movieList:List)->List:
        '''
        将电影id转换成电影信息
        :param movieList:
        :return:
        '''
        print("[%s] 正在解析电影" % time.ctime())
        ans = []
        for id in movieList:
            ans.append(self._movieInfo[int(id)])
        return ans
'''
有几个问题：
1. 时长为None
'''
if __name__ == '__main__':
    # 测试推荐
    # 7423
    feature = ""
    for i in range(32):
        feature += "0,"
    feature = feature[:-1]
    haveSeenMovies = [
        1306249,    # 唐伯虎点秋香
        1291543,    # 功夫
        1296201,    # 逃学威龙
        1298644,    # 赌圣
        1299680,    # 整蛊专家
        1306951,    # 鹿鼎记

    ]
    user = User("123",
                feature,
                haveSeenMovies,[])
    print(user.parseMovie(haveSeenMovies))
    for i in range(len(haveSeenMovies)):
        user.seeMovie(haveSeenMovies[i],8.0)

    # q = user.recommendBaseMovie(1299680)
    q = user.recommendMovies()
    print(type(q[0]))
    print(q)
    print(str(q))
    # q = user.recommendMovies()
    print(user.parseMovie(q))

    # for i in q:
    #     print(i)
    # 测试精排
    # l = [
    #         ['中国',2004,7.9,102,'喜剧'],
    #         ['中国',2014,8.9,109,'喜剧'],
    #         ['美国',2006,8.5,200,'战争'],
    #         ['日本',1990,9.6,109,'动作'],
    #         ['韩国',1999,7.6,120,'爱情'],
    #         ['美国',2001,5.4,119,'犯罪'],
    #         ['中国',2019,2.3,120,'犯罪'],
    #         ['日本',2020,1.2,121,'剧情'],
    #         ['韩国',2020,9.3,123,'喜剧'],
    #         ['日本',2010,3.4,98,'喜剧'],
    #         ['日本',2009,5.6,100,'剧情'],
    #         ['中国',2008,7.8,123,'剧情']
    # ]


    # 测试movies.csv
    # data = pd.read_csv(self._config.file_path_moviesInfomation_csv)
    # dicts = {}
    # for row in data.itertuples():
    #     dicts[int(getattr(row, 'id'))] = [
    #         getattr(row, 'year'), getattr(row, 'rating'), getattr(row, 'genre'),
    #         getattr(row, 'country'), getattr(row, 'duration')
    #     ]
    # print(dicts)
    # 测试国家转换
    # print(preProcessCountry(" 德a國12/32"))

    # 测试图数据库以及查询
    # graph = Graph(
    #     "http://localhost:7474",
    #     auth=("neo4j", "mikedean")
    # )
    # # 假定我们已经把两种node存进去了，label分别是Post和User,现在需要在他们间建立某关系
    #
    # node = graph.nodes.match('Movie', id=1291563).first()  # 找到id
    # print(node['name'])
    # print(node['duration'])
    # print(node['rating'])
    #
    # # 提取国家
    # cursor = graph.run("MATCH (m:Movie {id:%d})--(c:Country) RETURN c" % 1291544)
    # for record in cursor:
    #     tmp = str(record).replace("'","").replace(")","")
    #     print(tmp[tmp.find('value=')+len("value="):])
    #
    # # 提取年份
    # cursor = graph.run("MATCH (m:Movie {id:%d})--(c:Time) RETURN c" % 1291544)
    # for record in cursor:
    #     tmp = str(record).replace("'", "").replace(")", "")
    #     print(tmp[tmp.find('value=') + len("value="):])
    #
    # # 提取类型
    # cursor = graph.run("MATCH (m:Movie {id:%d})--(c:Genre) RETURN c" % 1291544)
    # for record in cursor:
    #     tmp = str(record).replace("'", "").replace(")", "")
    #     print(tmp[tmp.find('value=') + len("value="):])
