# POST/GET JSON

```python
# 初始化一个用户
# 请求内容
json = {
    'handleName': 'initialUser',		# 标识这个数据是用来请求新建用户的
    'userID': '12345',	# 用户的id 如果有下划线表明movies里面的是用户说的话
    'feature': '1,2,3,4,5,6,7,8,...'	# 用户的特征向量 这里可以为'None' 如果为'None' 则由我这边给出初始化
    'movies': '{1123:9.5,2234:10.0}'	# 用户看过的电影豆瓣id:评分
    'timeList': '[0,0,1,1,1,]'			# 与movies的顺序保持一致，相对时间
}
# 返回内容
rtn = {
    'status': 'success',				# 操作成功
    'feature': 'None',					# 如果请求的为None则返回一个特征向量，如果请求的不为None，则返回None
}
```



```python
# 推荐电影
# 请求内容
json = {
    'handleName' : 'recommendMovie',	# 处理的事务名称
    'number' : '50',					# 推荐电影的个数
    'way' : 'cos',						# 默认用余弦相似度/可以用distance作为另一个选择
}

# 返回内容
rtn = {
    'status' : 'success'				# 请求状态
    'movies' : '12393,12341,24124,24124'	# 返回推荐的电影豆瓣id 如果需要，我可以把电影的详细信息返回
}
```



```python
# 根据电影推荐电影
# 请求内容
json = {
    'handleName':'recommendMovieByMovie',	# 处理的事务名称
    'number': '50'							# 推荐电影的个数
    'id': '1234',							# 基准电影id
    'way' : 'cos',							# 默认用余弦相似度/可以用distance作为另一个选择
}

# 返回内容
rtn = {
    'status':'success',						# 请求状态
    'movies':'1234,4444,22141,342525'		# 返回推荐的电影豆瓣id
}
```



```python
# 更新feature
# 请求内容
json = {
    'handleName':'seeMovie',	# 事务的名称
    'id':'12341',	# 看过的电影id
    'score': '10.0'	# 评分
}
# 返回内容
rtn ={
    'status':'success',
    'feature':'123,1,2,4,2,4,4,3,5'
}
```





```
json = {'handleName' : 'recommendMovie','number' : '50','way' : 'cos'}

init_json = {'handleName': 'initialUser','userID': '12345','feature': 'None','movies':'{1306249:9.5,1291543:9.6,1296201:9.0,1298644:9.2,1299680:9.3,1306951:9.8}','timeList': '[0,0,1,1,1,1]'}
```

