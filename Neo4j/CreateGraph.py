from py2neo import Graph, Node, Relationship, Subgraph
import pandas as pd
import numpy as np

# 数据集路径名称
'''
    movies.csv 文件的summary列有空的，其余列都有值，无空行: id name year rating ratingsum img tags summary genre country
    person.csv 文件的sex、: id name img sex birthday birthplace summary
'''
path = ['../dataBase/source/movies.csv',
        '../dataBase/source/person.csv',
        '../dataBase/source/relationships-1.csv',
        '../dataBase/source/movies-v2.csv']
# 每一万条输出一次
OutputCnt = 1e4



def read(idx):
    '''
    读取数据并且返回
    :param idx: 索引
    :return:
    '''
    return pd.read_csv(path[idx])

def movieCsv(test_graph):
    '''
    处理movie.csv
    :parameter test_graph: neo4j图对象
    :return:
    '''
    data = read(0)
    print("1. 电影结点准备构建")
    # 标签、国家、上映时间、类型
    genre,country,tags,times = [],[],[],[]
    for row in data.itertuples():
        for v in getattr(row,'tags')[1:-1].replace("'","").split(","):
            tags.append(v)
        for v in getattr(row,'country').split("/"):
            country.append(v)
        for v in getattr(row,'genre').split("/"):
            genre.append(v)
        times.append(getattr(row,'year'))
    # 去除重复
    genre = list(set(genre))
    country = list(set(country))
    tags = list(set(tags))
    times = list(set(times))
    print("2. 数据处理完毕，开始构建")
    # 开始构建
    for g in genre:
        test_graph.create(Node("Genre",value=g))
    for c in country:
        test_graph.create(Node("Country", value=c))
    for t in tags:
        test_graph.create(Node("Tag", value=t))
    for t in times:
        test_graph.create(Node("Time", value=t))

    # Movie节点及关系
    cnt = 0
    all = len(data)
    for row in data.itertuples():
        cnt+=1
        print(cnt/all)
        film = Node("Movie",
                      id=getattr(row,'id'),name=getattr(row,'name'),
                      rating=getattr(row,'rating'),ratingSum=getattr(row,'ratingsum'),
                      img=getattr(row,'img'),summary=getattr(row,'summary'),
                      duration=105)
        for v in getattr(row,'tags')[1:-1].replace("'","").split(","):
            node = test_graph.nodes.match('Tag',value=v).first()
            test_graph.create(Relationship(film,'tag is',node))
        for v in getattr(row,'country').split("/"):
            node = test_graph.nodes.match('Country', value=v).first()
            test_graph.create(Relationship(film, 'country is', node))
        for v in getattr(row,'genre').split("/"):
            node = test_graph.nodes.match('Genre', value=v).first()
            test_graph.create(Relationship(film, 'genre is', node))
        node = test_graph.nodes.match('Time',value=getattr(row,'year')).first()
        test_graph.create(Relationship(film, 'time is', node))

    print("3. 电影结点构建完毕")


def personCsv(test_graph):
    '''
    处理person.csv
    :param test_graph: 图
    :return:
    '''
    data = read(1)
    all = len(data)
    cnt = 0
    for row in data.itertuples():
        cnt += 1
        print(cnt/all)
        Person = Node("Person",
                      id=getattr(row,'id'),img=getattr(row,'img'),
                      sex=getattr(row,'sex'),birthday=getattr(row,'birthday').split("/")[0],
                      summary=getattr(row,'summary'),birthplace=getattr(row,'birthplace'))
        test_graph.create(Person)

def relationshipCsv(test_graph):
    '''
    生成电影和人的关系,处理relationships.csv
    :param test_graph: 图
    :return:
    '''
    data = read(2)[2:]
    all = len(data)
    cnt = 0
    re = []
    for row in data.itertuples():
        cnt+=1
        if cnt%OutputCnt == 0:
            print("当前进度："+str(round(cnt/all,4)*100)+"%")
            print("正在递交")
            A = Subgraph(relationships=re)
            test_graph.create(A)
            re = []
            print("递交成功")
        filmId = getattr(row,'movie_id')
        personId = getattr(row,'person_id')
        relationName = getattr(row,'role')
        film = test_graph.nodes.match('Movie',id=filmId).first()
        person = test_graph.nodes.match('Person',id=personId).first()
        try:
            re.append(Relationship(film, str(relationName), person))
        except:
            print("错误")

    print("加载完毕")

def addDuration(test_graph):
    '''
    为每个电影增加时长
    :param test_graph: 数据库
    :return:
    '''
    data = read(3)
    all = len(data)
    cnt = 0
    for row in data.itertuples():
        cnt+=1
        node = test_graph.nodes.match('Movie',id=getattr(row,'id')).first()
        node['duration']=getattr(row, 'duration')
        test_graph.push(node)
        if cnt%500==0:
            print("当前进度"+str(cnt/all))
    print("done")

def addPersonName(test_graph):
    '''
    为每个演员增加姓名
    :param test_graph: 数据库
    :return:
    '''
    print("正在写")
    data = read(1)
    all = len(data)
    cnt = 0
    for row in data.itertuples():
        cnt+=1
        node = test_graph.nodes.match('Person',id=getattr(row,'id')).first()
        node['name']=getattr(row, 'name')
        test_graph.push(node)
        if cnt%500==0:
            print("当前进度"+str(cnt/all))
    print("done")

def addName(test_graph):
    '''
    :param test_graph:
    :return:
    '''
    # data = read()
    pass

if __name__ == '__main__':
    # 连接py2neo
    test_graph = Graph(
        "http://localhost:7474",
        auth=("neo4j","mikedean")
    )
    # test_graph.delete_all() # 谨慎使用
    # relationshipCsv(test_graph)
    # 8:44
    # addDuration(test_graph)
    # addPersonName(test_graph)