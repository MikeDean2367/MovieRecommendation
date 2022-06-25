# Readme

本代码为课程设计的后端代码，项目的总体框架可以参考`答辩.pptx`。

## Cuda

采用`cuda`编写的加速程序，使用方法如下

```
matrix.exe num user-vector cal-way
```

此处的`user-vector`为特征向量，该程序中为32维向量，一个例子：`1.00,-1.02,0.002,...`；

此处的`num`为召回电影的个数；

此处的`cal-way`为计算向量相似度的衡量方法，可选`cosine`和`distance`，分别对应于余弦相似度和两个向量的距离。



## DialogMachine

对话机器人框架，安装和使用方法可以参考[此处](https://github.com/MikeDean2367/MovieChatBot)。



## MovieFeatureEmbedding

将电影、演员嵌入为向量，采用`TransD`嵌入方法，此处设置的维度为32维，电影的嵌入结果保存在`movies_vector.txt`。



## Neo4j

搭建电影知识图谱的辅助代码。



## RecommendAlgorithm

推荐算法，主要代码存储在`recommendAlgorithm.py`。

由于该仓库为后端部分，且后端和前端不属于同一个机器，因此搭建本地服务器，前端通过`post`和`get`的方式来和后端进行通信，代码保存在`server.py`文件中。

具体的算法可以参考`第四次报告.pptx`。