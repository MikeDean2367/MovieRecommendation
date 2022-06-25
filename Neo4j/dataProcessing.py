'''
完善电影简介
完善电影时长
增加电影评分内容
电影名称	评分	评价人数	5星人数	4星人数	3星人数	2星人数	1星人数	短评数量	影评数量	类型	导演	编剧	主演	制片国家/地区	语言	上映日期	片长	豆瓣网址	官方网址	IMDb链接	宣传海报链接	剧情简介	总分（评分×评价人数）
https://movie.douban.com/subject/1292052/
'''
import time

import pandas as pd


if __name__ == '__main__':
    path = ['../dataBase/source/movies.csv',
            '../dataBase/source/movies.xlsx']
    csv = pd.read_csv(path[0])
    xls = pd.read_excel(path[1])
    ans = []
    j = 0
    c = 0
    for i in range(len(csv)):
        # 获取csv的id
        csvId = int(getattr(csv[i:i+1],'id'))
        xlsId = int(getattr(xls[j:j+1],'ID'))
        while csvId>xlsId:
            j += 1
            xlsId = int(getattr(xls[j:j + 1], 'ID'))
        if csvId==xlsId:
            ans.append(str(float(getattr(xls[j:j+1],'片长').values)))
        else:
            ans.append("None")
            c+=1
            # print(csvId)
        j += 1
    with open("time.txt","w") as f:
        f.writelines("\n".join(ans))
    print("done")
    print(c)

