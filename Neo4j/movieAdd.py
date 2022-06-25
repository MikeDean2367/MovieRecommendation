# 填补空的简介
import requests
import time
url = 'https://movie.douban.com/subject/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

def GetMiddleStr(content,startStr,endStr):
    startIndex = content.find(startStr)
    if startIndex>=0:
        endIndex = content[startIndex:].find(endStr)+startIndex
        startIndex += len(startStr)
    else:
        startStr = '<span property="v:summary">'
        startIndex = content.find(startStr)
        if startIndex>=0:
            endIndex = content[startIndex:].find(endStr) + startIndex
            startIndex += len(startStr)
        else:
            return None
    # return str.strip(content[startIndex:endIndex])
    return str.strip(content[startIndex:endIndex].replace("<br />", "").replace('\n', '').replace('\r', '').replace("  ", ""))

def findSummary():
    id = []
    with open("../第二次/缺失MovieId.txt","r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            id.append(line)
    for i in id:
        response = requests.get(url=url+i+"/", headers=headers)
        s = str(response.text)
        t = GetMiddleStr(s, '<span property="v:summary" class="">', "</span>")
        if t==None:
            for j in range(5):
                time.sleep(3)
                response = requests.get(url=url + i + "/", headers=headers)
                s = str(response.text)
                t = GetMiddleStr(s, '<span property="v:summary" class="">', "</span>")
                if t != None:
                    break
        print(t)
        # print(GetMiddleStr(s, '<span property="v:runtime" content="', '">'))

def findTime():
    id = []
    with open("../第二次/MovieId.txt","r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            id.append(line)
    ans = []
    cnt = 0
    for i in id:
        response = requests.get(url=url+i+"/", headers=headers)
        s = str(response.text)
        t = GetMiddleStr(s, '<span property="v:runtime" content="', '">')
        ans.append(t)
        cnt += 1
        print(cnt)
    with open("../第二次/MovieTime.txt", "w") as f:
        f.writelines("\n".join(ans))


if __name__ == '__main__':
    findSummary()

