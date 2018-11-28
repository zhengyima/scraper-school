#!/usr/bin/python3
# coding=gbk

import pymongo
import csv
import urllib3
import json


def findSchoolNews(sname_zn):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:38018/")
    mydb = myclient["216SchoolNews"]
    mycol = mydb["news_bit"]
    myquery = {"sname_zh": sname_zn}
    res = mycol.find(myquery)
    return res


    # cnt = 0
    # for x in res:
    #    cnt += 1
    # print(x)

    # print(cnt)


http = urllib3.PoolManager()

f = open('/home/dou/schoolrank/tutorial/tutorial/spiders/school.csv', "r")
dict_reader = csv.DictReader(f)
schools = {}
for row in dict_reader:
    schools[row['name_zh']] = row
f.close()

countResult = []
countPositiveResult = []
for sname_zh in schools:
    print(sname_zh)
    res_school = []
    res_positive_school = []
    school_row = schools[sname_zh]
    schoolMongoCursor = findSchoolNews(sname_zh)
    schoolMongoResult = []
    for everyNews in schoolMongoCursor:
        schoolMongoResult.append({"content": everyNews['content']})

    # for everyNews in schoolMongoResult:
    #    content = everyNews['content']
    #    for schoolCandidate in schools:
    #        if schoolCandidate in content:
    for schoolMentionedCandidate in schools:

        MentionedCount = 0
        PositiveCount = 0
        for everyNews in schoolMongoResult:
            if schoolMentionedCandidate in everyNews['content']:
                r = http.request("GET", "http://183.174.228.47:8282/RUCNLP/neural/sentiment",fields={"doc": "11月14日晚，北京大学经济学院“诺奖得主面对面”系列活动学术讲座在学院东旭学术报告厅举行。"})
                print(everyNews['content'])
                print(r.data)
                sentimentScore = json.loads(r.data)["Score"]
                if int(sentimentScore) >= 0:
                    PositiveCount += 1
                MentionedCount += 1
        res_school.append(str(MentionedCount))
        res_positive_school.append(str(PositiveCount))
        # print("sname_zh:"+sname_zh)
        # print("schoolMentionedCandidate:"+schoolMentionedCandidate)
        # print(MentionedCount)
        # print("\n\n\n")

    print(res_school)
    print(res_positive_school)
    countResult.append(res_school)
    countPositiveResult.append(res_positive_school)

f = open('/home/dou/schoolrank/tutorial/tutorial/spiders/CountMatrix.csv', "a")
myWriter = csv.writer(f)
firstRow = [""]
for sname_zh in schools:
    firstRow.append(sname_zh)
myWriter.writerow(firstRow)

for rowIndex in range(0, len(schools)):
    schoolName = firstRow[1 + rowIndex]
    Arow = [schoolName]
    Arow += countResult[rowIndex]
    myWriter.writerow(Arow)

f.close()

f = open('/home/dou/schoolrank/tutorial/tutorial/spiders/CountPositiveMatrix.csv', "a")
myWriter = csv.writer(f)
firstRow = [""]
for sname_zh in schools:
    firstRow.append(sname_zh)
myWriter.writerow(firstRow)

for rowIndex in range(0, len(schools)):
    schoolName = firstRow[1 + rowIndex]
    Arow = [schoolName]
    Arow += countPositiveResult[rowIndex]
    myWriter.writerow(Arow)

f.close()


