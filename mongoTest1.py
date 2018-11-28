#!/usr/bin/python3

import pymongo
import csv


def findSchoolNews(sname_zn):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:38018/")
    mydb = myclient["216SchoolNews"]
    mycol = mydb["news"]
    myquery = {"sname_zh": sname_zn}
    res = mycol.find(myquery)
    return res


    # cnt = 0
    # for x in res:
    #    cnt += 1
    # print(x)

    # print(cnt)


f = open('/home/dou/schoolrank/tutorial/tutorial/spiders/school.csv', "r")
dict_reader = csv.DictReader(f)
schools = {}
for row in dict_reader:
    schools[row['name_zh']] = row
f.close()

countResult = []
countSchools = []
for sname_zh in schools:
    print(sname_zh)
    res_school = []
    school_row = schools[sname_zh]
    schoolMongoCursor = findSchoolNews(sname_zh)
    schoolMongoResult = []
    for everyNews in schoolMongoCursor:
        schoolMongoResult.append({"content": everyNews['content']})
    countSchools.append(str(len(schoolMongoResult)))
    # for everyNews in schoolMongoResult:
    #    content = everyNews['content']
    #    for schoolCandidate in schools:
    #        if schoolCandidate in content:
    for schoolMentionedCandidate in schools:

        MentionedCount = 0
        for everyNews in schoolMongoResult:
            if schoolMentionedCandidate in everyNews['content']:
                MentionedCount += 1
        res_school.append(str(MentionedCount))
        # print("sname_zh:"+sname_zh)
        # print("schoolMentionedCandidate:"+schoolMentionedCandidate)
        # print(MentionedCount)
        # print("\n\n\n")

    print(res_school)
    countResult.append(res_school)

f = open('/home/dou/schoolrank/tutorial/tutorial/spiders/CountMatrix.csv', "a")
myWriter = csv.writer(f)
firstRow = ["","News Nums"]
for sname_zh in schools:
    firstRow.append(sname_zh)
myWriter.writerow(firstRow)

for rowIndex in range(0, len(schools)):
    schoolName = firstRow[2 + rowIndex]
    Arow = [schoolName+"("+countSchools[rowIndex]+")",countSchools[rowIndex]]
    Arow += countResult[rowIndex]
    myWriter.writerow(Arow)

f.close()


