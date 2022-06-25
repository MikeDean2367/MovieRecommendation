import requests
import json
import http.client

if __name__ == '__main__':
    '''
        1306249,    # 唐伯虎点秋香
        1291543,    # 功夫
        1296201,    # 逃学威龙
        1298644,    # 赌圣
        1299680,    # 整蛊专家
        1306951,    # 鹿鼎记
        1306249:9.5,1291543:9.6,1296201:9.0,1298644:9.2,1299680:9.3,1306951:9.8
    '''
    url = "http://localhost:9977/TestServer"
    init_json = {
        'handleName': 'initialUser',  # 标识这个数据是用来请求新建用户的
        'userID': '12345',  # 用户的id
        'feature': 'None',  # 用户的特征向量 这里可以为'None' 如果为'None' 则由我这边给出初始化
        'movies': '{1306249:9.5,1291543:9.6,1296201:9.0,1298644:9.2,1299680:9.3,1306951:9.8}',  # 用户看过的电影豆瓣id:评分
        'timeList': '[0,0,1,1,1,1]'  # 与movies的顺序保持一致，相对时间
    }
    init_json_new = {
        'handleName': 'initialUser',  # 标识这个数据是用来请求新建用户的
        'userID': '12345_',  # 用户的id
        'feature': 'None',  # 用户的特征向量 这里可以为'None' 如果为'None' 则由我这边给出初始化
        'movies': '西域男孩、战狼、唐伯虎点秋香、指环王',  # 用户看过的电影豆瓣id:评分
        'timeList': '[0,0,1,1,1,1]'  # 与movies的顺序保持一致，相对时间
    }
    recommend_json = {
        'handleName': 'recommendMovie',  # 处理的事务名称
        'number': '50',  # 推荐电影的个数
        'way': 'cos',  # 默认用余弦相似度/可以用distance作为另一个选择
    }
    recommend_by_movie_json = {
        'handleName': 'recommendMovieByMovie',  # 处理的事务名称
        'number': '50',  # 推荐电影的个数
        'id': '1299680',  # 基准电影id
        'way': 'cos',  # 默认用余弦相似度/可以用distance作为另一个选择
    }
    feature_json = {
        'handleName': 'seeMovie',  # 事务的名称
        'id': '12341',  # 看过的电影id
        'score': '10.0'  # 评分
    }
    r = requests.post(url, data=json.dumps(init_json_new))
    # r = requests.post(url, data=json.dumps(recommend_json))
    # r = requests.post(url, data=json.dumps(recommend_by_movie_json))
    print(r.text)