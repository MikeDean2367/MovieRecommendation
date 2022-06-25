import time

import recommendAlgorithm as rcmd
from typing import AnyStr
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import demjson as dj
import pandas as pd
from langconv import *
user = None
path_csv = "moviesInformation.csv"
class S(BaseHTTPRequestHandler):

    def __init__(self,request,client_address,server):
        global user
        print("restart")
        print(user)
        self.data = None    # 请求头的内容,dict
        super(S, self).__init__(request,client_address,server)

    def _movieName2Id(self,message):
        '''
        将电影名称转换成id
        :param message:
        :return:
        '''
        separator = ''
        if '、' in message:
            separator = '、'
        elif ',' in message:
            separator = ','
        elif '，' in message:
            separator = '，'
        elif ' ' in message:
            separator = ' '
        movies = str.split(message, separator)
        print(movies)
        data = pd.read_csv(path_csv)
        ans = []
        database = data['name'].tolist()
        for movie in movies:
            for i in range(len(database)):
                if movie in database[i] or Converter('zh-hant').convert(movie) in database[i]:
                    ans.append(data['id'][i])
        return ans

    def _createUser(self):
        '''
        创建用户
        :return: 返回内容
        '''
        global user
        rtn = {}
        # 新加入的■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        if "_" in self.data['userID']:
            # 需要调用那个啥
            print("执行电影转id")
            id = self._movieName2Id(self.data['movies'])
            dicts = {}
            # 添加评分
            print(id)
            for i in id:
                dicts[int(i)] = 9.0
            print("原始movies",self.data['movies'])
            self.data['movies'] = str(dicts)
            print("转换后:",self.data['movies'])
        # 新加入的■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        # 下面改了这个userID的id
        user = rcmd.User(userId=self.data['userID'][:-1],feature=self.data['feature'],
                        movies=dj.decode(self.data['movies']),time_=list(eval(self.data['timeList'])))
        feature = None
        if self.data['feature']=="None":
            feature = user.initialFeature()
        if user != None:
            rtn['status'] = 'success'
        else:
            rtn['status'] = 'fail'
        if feature==None:
            rtn['feature'] = 'None'
        else:# 如果传入的feature为None
            rtn['feature'] = feature
        return rtn

    def _recommendMovie(self)->dict:
        '''
        推荐电影,此处没有对计算相似度进行更新，因此data中的way暂时没有用到
        :return:dict
        '''
        global user
        rtn = {}
        number = int(self.data['number'])   # 返回电影个数
        if user!=None:
            lists = str(user.recommendMovies(number=number))
            if lists==None:
                print("[%s] 推荐失败，具体原因查看代码！" % time.ctime())
                rtn['status'] = 'fail'
                rtn['movies'] = 'None'
            else:
                rtn['status'] = 'success'
                rtn['movies'] = lists[1:-1] # 去除开头和结尾的括号
        else:
            print("[%s] 没有创建用户，请创建后操作！" % time.ctime())
            rtn['status'] = 'fail'
            rtn['movies'] = 'None'
        return rtn

    def _recommendMovieByMovie(self)->dict:
        '''
        根据电影推荐电影
        :return:
        '''
        global user
        rtn = {}
        number = int(self.data['number'])  # 返回电影个数
        id = int(self.data['id'])   # 推荐的电影id
        lists = None
        if user != None:
            lists = str(user.recommendBaseMovie(movieId=id,number=number))
            if lists == None:
                print("[%s] 推荐失败，具体原因查看代码！" % time.ctime())
                rtn['status'] = 'fail'
                rtn['movies'] = 'None'
            else:
                rtn['status'] = 'success'
                rtn['movies'] = lists[1:-1]  # 去除开头和结尾的括号
        else:
            print("[%s] 没有创建用户，请创建后操作！" % time.ctime())
            rtn['status'] = 'fail'
            rtn['movies'] = 'None'
        return rtn

    def _updateFeaure(self)->dict:
        '''
        更新特征向量
        :return: feature
        '''
        global user
        rtn = {}
        id = int(self.data['id'])
        score = float(self.data['score'])
        if user!=None:
            feature = user.seeMovie(movieId=id,score=score)
            if feature==None:
                print("[%s] 更新失败，具体原因查看代码！" % time.ctime())
                rtn['status'] = 'fail'
                rtn['feature'] = 'None'
            else:
                rtn['status'] = 'success'
                rtn['feature'] = feature
        else:
            print("[%s] 没有创建用户，请创建后操作！" % time.ctime())
            rtn['status'] = 'fail'
            rtn['feature'] = 'None'
        return rtn

    def _messageHandler(self, data:AnyStr):
        '''
        处理消息
        :param data:
        :return:
        '''
        rtn = {}    # 返回值
        self.data = jsons = dj.decode(data)
        functions = [self._createUser, self._recommendMovie,self._recommendMovieByMovie,self._updateFeaure]
        handleName = ['initialUser','recommendMovie','recommendMovieByMovie','seeMovie']
        idx = handleName.index(jsons['handleName'])
        rtn = functions[idx]()
        print(rtn)
        return str(rtn)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        paths = {
            '/foo': {'status': 200},
            '/bar': {'status': 302},
            '/baz': {'status': 404},
            '/qux': {'status': 500}
        }
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        rtn = self._messageHandler(data)
        if self.path in paths:
            self.respond({'status': 200})
            # self.respond(paths[self.path])
        else:
            self.respond({'status': 500})
        # logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.wfile.write(rtn.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself

        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        # print(type(post_data.decode('utf-8')),post_data.decode('utf-8'))
        rtn = self._messageHandler(post_data)
        res = "You Input: " + post_data.decode('utf-8')
        self.do_HEAD()
        # self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        # self.wfile.write("{}".format(res).encode('utf-8'))
        self.wfile.write(rtn.encode('utf-8'))
        # self.wfile.write("POST request for {ASS}".format(data).encode('utf-8'))

    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.wfile.write(response)

    def handle_http(self, status_code, path):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = '''
           <html><head><title>Title goes here.</title></head>
           <body><p>This is a test.</p>
           <p>You accessed path: {}</p>
           </body></html>
           '''.format(path)
        content = ""
        return bytes(content, 'UTF-8')

def run(server_class=HTTPServer, handler_class=S, port=9977):
    print("run()")
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("httpd.server_close()")
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    '''
    默认端口为9977
    '''
    from sys import argv

    # if len(argv) == 2:
    #     run(port=int(argv[1]))
    # else:
    user = None
    run()
