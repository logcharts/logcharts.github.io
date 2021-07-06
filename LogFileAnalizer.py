# -*- coding: utf-8

import re
import json
import sys
import os
import time
import requests

#支持的日志正则(分析工具会自动判断用哪个)
patternList= (
    #module-hrs-register-web, 等
    "^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s?(\[.*?\])\s?(\w*?)\s+([\w?\.$]+)(\(\d+\))? (.*)",
    #his-doc-work-service 等
    "^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s?(\[.*?\])\s?(\w*?)\s+([\w?\.$]+)(\(\d+\))?\s+(.*)"
)
#时间戳转日期
def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',timeStruct)

#获取文件的大小,结果保留两位小数，单位为MB'''
def getFileSize(filePath):
    filePath = unicode(filePath,'utf8')
    fsize = os.path.getsize(filePath)
    unit = 'B'
    if fsize > 1024 :
        fsize = fsize/float(1024)
        unit = 'KB'
    if fsize > 1024 :
        fsize = fsize/float(1024)
        unit = 'MB'
    if fsize > 1024 :
        fsize = fsize/float(1024)
        unit = 'GB'
    return str(round(fsize,2))+' '+unit
#获取文件的创建时间
def getFileCreateTime(filePath):
    filePath = unicode(filePath,'utf8')
    t = os.path.getctime(filePath)
    return TimeStampToTime(t)

#获取文件的修改时间
def getFileModifyTime(filePath):
    filePath = unicode(filePath,'utf8')
    t = os.path.getmtime(filePath)
    return TimeStampToTime(t)

#获取文件行数
def lineCount( file ):
    count=0
    thefile=open(filePath)
    while True:
        buffer=thefile.read(1024*8192)
        if not buffer:
            break
        count+=buffer.count('\n')
    thefile.close()
    return count

#尝试从最多前100行判断日志格式
def getPattern( filePath ):
    f = open(filePath)
    lineNum = 0;
    logLine = f.readline()               # 调用文件的 readline()方法
    while logLine:
        lineNum = lineNum + 1
        if lineNum > 100 :
            break
        #不以日期开头的略过
        if not re.match("^\d{4}-\d{2}-\d{2}", logLine) :
            continue
        #逐个正则尝试
        for pattern in patternList:
            matchResult = re.match(pattern, logLine)
            if matchResult:
                return pattern

    f.close()
    print "没有匹配到合适的分析正则, 请确认日志文件正确, 再联系开发补全脚本中的日志正则"
    exit(1)

def putData(thisData, mapKey, charCount, times):
    if mapKey in thisData :
        loggerData=thisData[mapKey]
        loggerData["lineCount"]=loggerData["lineCount"]+1
        loggerData["times"]=loggerData["times"]+times
        loggerData["charCount"]=loggerData["charCount"]+charCount
    else :
        thisData[mapKey]={"lineCount":1, "charCount":charCount, "times":1}
    return

#---------------开始处理-----
#获取和校验文件
if len(sys.argv) < 2 :
    print "请在命令中指定文件,如: python LogFileAnalizer.py some-project.log"
    exit(1)
filePath=sys.argv[1]
if not filePath.endswith(".log") | filePath.endswith(".txt") :
    confirm = raw_input("文件后缀不像是文本,如果是压缩文件请先手动解压,确定继续分析吗? (y/n): ")
    print(confirm)
    if not confirm == "y" :
        exit(0)
#尝试从最多前100行判断日志格式
print('校验日志格式...')
pattern = getPattern(filePath)


print('获取总行数...')
count=lineCount(filePath)
print("总行数:" + str(count))


#最后Logger
lastLogger= "unknown"
#最后Logger的代码行数
lastLoggerLine= "None"
#最后级别
lastLevel="INFO"
#最后小时
lastHour="0000-00-00 00"

#入口数据
pointCutData={lastLogger + ":" + str(lastLoggerLine):{"lineCount":0, "charCount":0, "times":0}}
#级别数据
logLevelData={'INFO':{"lineCount":0, "charCount":0, "times":0}}
#小时数据
hourData={}


# logLine = "2021-06-30 16:18:30[qtp993370665-135151]ERROR c.g.d.c.cluster.DitingTagInvoker.invoke$original$2eHCwhWc Failed to invoke the method listShiftCasesForStd in the service com.greenline.hrs.biz.service.ShiftCaseService. Maybe No provider available for the service com.greenline.hrs.biz.service.ShiftCaseService:*:* from registry xingyinacos.guahao.cn:80,xingyinacos.guahao.cn:80,xingyinacos.guahao.cn:80 on the consumer 10.20.84.191 using the dubbo version 2.7.3. Please check if the providers have been started and registered, or has been isolated.org.apache.dubbo.rpc.RpcException: Failed to invoke the method listShiftCasesForStd in the service com.greenline.hrs.biz.service.ShiftCaseService. Tried 1 times of the providers [10.20.105.35:28090] (1/12) from the registry 10.12.1.66:2181 on the consumer 10.20.84.191 using the dubbo version 2.7.3. Last error is: 接口异常"


print('开始扫描...')

f = open(filePath)
logLine = f.readline()               # 调用文件的 readline()方法
while logLine:
    charCount=len(logLine)
    matchResult = re.match(pattern, logLine)
    if matchResult:
        # print "matchObj.group(1) : ", matchResult.group(1)
        # print "matchObj.group(2) : ", matchResult.group(2)
        # print "matchObj.group(3) : ", matchResult.group(3)
        # print "matchObj.group(4) : ", matchResult.group(4)
        # print "matchObj.group(5) : ", matchResult.group(5)
        # print "matchObj.group(6) : ", matchResult.group(6)
        # exit(0

        lastLogger=matchResult.group(4)
        lastLoggerLine=matchResult.group(5)
        lastHour=matchResult.group(1)[0:13]
        lastLogLevel=matchResult.group(3)

        mapKey=lastLogger+":"+str(lastLoggerLine)
        putData(pointCutData, mapKey, charCount, 1)
        putData(hourData, lastHour, charCount, 1)
        putData(logLevelData, lastLogLevel, charCount, 1)

    else:
        mapKey=lastLogger+":"+str(lastLoggerLine)
        putData(pointCutData, mapKey, charCount, 0)
        putData(hourData, lastHour, charCount, 0)
        putData(logLevelData, lastLogLevel, charCount, 0)
    logLine = f.readline()

f.close()
print('扫描完成')
basicInfo={"fileName":filePath,
           "fileSize":getFileSize(filePath),
           "fileCreateTime":getFileCreateTime(filePath),
           "fileModifyTime":getFileModifyTime(filePath)}
finalData={"basicInfo":basicInfo,"pointCutData":pointCutData,"hourData":hourData,"logLevelData":logLevelData}

#上传数据
headers = {'Content-Type':'application/json'}
rep = requests.post(url='https://api.e5cm.xyz/weapp/cache/setTemp', data=json.dumps(finalData), headers=headers)
print('Please visit the url below to check analyze result(valid for 24h): \nhttps://logcharts.github.io?key='+rep.text)

# print(json.dumps(finalData))

