# 将电影名称转成id

import pandas as pd
from langconv import *

path_csv = "moviesInformation.csv"

def convert(message:str):
    # 输入的是字符串
    separator = ''
    if '、' in message:
        separator = '、'
    elif ',' in message:
        separator = ','
    elif '，' in message:
        separator = '，'
    elif ' ' in message:
        separator = ' '
    movies = str.split(message,separator)
    print(movies)
    data = pd.read_csv(path_csv)
    ans = []
    database = data['name'].tolist()
    for movie in movies:
        for i in range(len(database)):
            if movie in database[i] or Converter('zh-hant').convert(movie) in database[i]:
                ans.append(data['id'][i])
    return ans
if __name__ == '__main__':
    print(convert("唐伯虎点秋香、战狼"))