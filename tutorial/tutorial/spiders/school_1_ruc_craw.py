import scrapy

import datetime
import csv
import urllib3
import json
import time
import re
import traceback

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc


class rucSpider(scrapy.Spider):
    name = "ruc"
    http =  urllib3.PoolManager()

    def __init__(self, category=None, *args, **kwargs):
        super(rucSpider, self).__init__(*args, **kwargs)
        f = open('/home/dou/schoolrank/tutorial/tutorial/spiders/format.csv',"r")
        dict_reader = csv.DictReader(f)
        self.formas = {}
        for row in dict_reader:
            self.formas[row['id']] = row


    def start_requests(self):
        for id in self.formas:
            #print("#################"+self.formas[id]["name_zh"]+self.formas[id]["disabled"]+"#################")
            try:
                if self.formas[id]["disabled"] == "79":
                    if self.formas[id]["news_list_dynamic"] == "0":
                        yield scrapy.Request(url=self.formas[id]['url'], meta={'id': id}, callback=self.parse)
                    else:
                        yield scrapy.Request(url=self.formas[id]['url'], meta={'id': id}, callback=self.parse_dynamic)
            except:
                pass

    def parseNews(self, response):

        #print(response.text)
        id = response.meta['id']

        #print("$$$$$$$$$$$$$$$")
        #print(response.meta)

        if "title" in response.meta:
            title = response.meta["title"]
        else:
            title = response.css(self.formas[id]['news_title']).extract_first()

        if "date" in response.meta:
            date = response.meta["date"]
        else:
            if str(self.formas[id]["news_date_multi"]) == "1":
                date = "\\n".join(response.css(self.formas[id]['news_date']).extract()[0:])
            else:
                date = response.css(self.formas[id]['news_date']).extract_first()

        if "view" in response.meta:
            view = response.meta["view"]
        else:
            try:
                view = response.css(self.formas[id]['news_view']).extract_first()
            except:
                view = ""
        try:
            source = response.css(self.formas[id]['news_source']).extract_first()
        except:
            source = ""
        try:
            author = ",".join(response.css(self.formas[id]['news_author']).extract())
        except:
            author = ""

        #print(self.formas[id]['news_content'])
        content = "\\n".join(response.css(self.formas[id]['news_content']).extract()[0:])
        base_url = get_base_url(response)
        yield {"sid":id,"sname":self.formas[id]['name'],"sname_zh":self.formas[id]["name_zh"],"type":self.formas[id]["type"],"title":title,"date":date,"view":view,"source":source,"author":author,"content":content,"url":base_url,"craw_time":datetime.datetime.now()}

    def parse(self, response):
        try:
            id = response.meta['id']
            print("----------------"+str(id)+"------------------------")
            #print(response.url)
            #print(response.text)
            #print(self.formas[id]['news_list'])
            print(len(response.css(self.formas[id]['news_list'])))

            for new in response.css(self.formas[id]['news_list']):

                #print("----------------" + str(id) + "------------------------")
                #yield {
                #    'name': teacher.css('div.name a::text').extract_first(),
                #    'homepage':  teacher.css('div.name a::attr("href")').extract_first(),
                #    "research":",".join(teacher.css('div.research p::text').extract())
                #}

                homepage = new.css(self.formas[id]["news_a_href"]).extract_first()
                try:
                    if ("218.193.144.95" in homepage) or (self.formas[id]["name"] == "ecust" and "category" not in homepage):
                    #if self.formas[id]["name"] == "ecust" and "category" not in homepage:
                        print("**************************************************************************")
                        continue
                except:
                    pass
                meta_data = {'id':id}
                try:
                    meta_data['title'] = new.css(self.formas[id]['new_list_title']).extract_first()
                except:
                    title = ""

                try:
                    meta_data['date'] = new.css(self.formas[id]['news_list_date']).extract_first()
                    #print(meta_data)
                except:
                    date = ""
                #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print(homepage)
                #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

                try:
                    yield response.follow(homepage, meta=meta_data,callback=self.parseNews)
                except:
                    continue

            url_prefix = self.formas[id]["url_prefix"]
            xp = response.css(self.formas[id]["news_list_next_page_a_href"]).extract_first()


            print(xp)
            print("\n\n\n\n")


            yield response.follow(xp, meta={'id':id},callback=self.parse)
        except Exception as e:
            traceback.print_exc()
            info = traceback.format_exc()
            pass




    def parse_dynamic(self, response):
        try:
            id = response.meta['id']
            url_prefix = self.formas[id]["url_prefix"]
            if id=="3": #thu
                for year in range(2012,2019):
                    for month in range(1,13):
                       try:
                           res = json.loads(self.http.request("GET", "http://news.tsinghua.edu.cn/publish/thunews/newsCollections/d_"+str(year)+"_"+str(month)+".json").data)
                           for day in res["data"]:
                               news_day_list =  res["data"][day]
                               for news_day in news_day_list:
                                   yield response.follow(url_prefix+news_day["htmlurl"].replace(".html","_.html"),meta={"id":id,"title":news_day["title"],"date":datetime.date(year,month,int(day)).strftime("%Y-%m-%d")},callback=self.parseNews)
                       except:
                           pass
            if id == "7":  # thu
                for year in range(2012, 2019):
                    for month in range(1, 13):
                        try:
                            res = json.loads(self.http.request("GET","http://news.bnu.edu.cn/jsonData/d_" + str(year) + "_" + str(month) + ".json").data)
                            for day in res["data"]:
                                news_day_list = res["data"][day]
                                for news_day in news_day_list:
                                    yield response.follow(url_prefix + news_day["htmlurl"].replace(".html", "_.html"),meta={"id": id, "title": news_day["title"],"date": datetime.date(year, month, int(day)).strftime("%Y-%m-%d")}, callback=self.parseNews)
                        except:
                            pass
            elif id=="82":  #shishu
                page = 1
                res = self.parse_shishu(page)
                while len(res['Message'])>0 and page<10000:
                    for message in res['Message']:
                        yield response.follow(url_prefix+message['FriendlyLink'],meta={"id":id,"title":message['Title'],"date":message['PublishDate']},callback=self.parseNews)
                    page += 1
                    print(page)
                    res = self.parse_shishu(page)
            elif id=="99":
                page = 1
                res = self.parse_njnu(page)
                while len(res)>0 and page<10000:
                    for url in res:
                        yield response.follow(url,meta={"id":id},callback=self.parseNews)
                    page += 1
                    print(page)
                    res = self.parse_njnu(page)
            elif id=="104":
                page = 1
                res = self.parse_ncu(page)
                while len(res)>0 and page<10000:
                    for item in res:
                        yield response.follow(item["url"],meta={"id":id,"view":item["view"],"date":item["date"]},callback=self.parseNews)
                    page += 1
                    res = self.parse_ncu(page)
            elif id=="56":
                page = 1
                res = self.parse_cfau(page)
                while len(res)>0 and page<10000:
                    for item in res:
                        print(url_prefix+item["url"])
                        yield response.follow(url_prefix+item["url"],meta={"id":id,"date":item["date"]},callback=self.parseNews)
                    page += 1
                    res = self.parse_cfau(page)
        except:
            pass

    def parse_shishu(self, page):
        time.sleep(1)
        jflag = 1
        while jflag:
            r = self.http.request("POST","http://news.shisu.edu.cn/WebSiteManage/Home/NewGetContentDtosOnTheFrontPage2",fields={"pageSize":12,"page":page})
            try:
                dict = json.loads(r.data)
                dict['Message'] = json.loads(dict['Message'])
                jflag = 0
            except:
                print("some json error!")
                print(r.data)
                dict = {}
                dict['Message'] = []
                jflag = 1
                time.sleep(10)
        return dict

    def parse_njnu(self,page):
        r = self.http.request("GET","http://sun.njnu.edu.cn/manage/get_info_yb.aspx?file=FY162300_518369&idinfo=111418_305585&page="+str(page))
        while int(r.status)!=200:
            time.sleep(10)
            r = self.http.request("GET","http://sun.njnu.edu.cn/manage/get_info_yb.aspx?file=FY162300_518369&idinfo=111418_305585&page="+str(page))
        urls = []
        for m in re.split("</li>", r.data.decode("utf-8")):
            start = m.find("http")
            end = m.find(".html\"") + 5
            if len(m[start:end])==0:
                break
            urls.append(m[start:end])
        return urls

    def parse_ncu(self,page):
        print("ncu-----------------"+str(page)+"--------------")
        #time.sleep(3)
        ncu_postfields = {
            "siteId": "074455556923",
            "classId": "730413625311",
            "tempPath": "nandanews/ROOT/html\\ndyw\massInserted.js",
            "pageSize": 22,
            "currPage": page,
            "pageTotal": 331,
            "recordCount": 7276,
            "str_NewsType": "null",
            "str_ListType": "News",
            "str_isSub": "true",
            "str_Desc": "null",
            "str_DescType": "null",
            "str_isDiv": "true",
            "str_ulID": "null",
            "str_ulClass": "null",
            "str_bfStr": "0|5|lastnews",
            "str_isPic": "null",
            "str_NaviNumber": "null",
            "str_TitleNumer": 30,
            "str_ContentNumber": "null",
            "str_ShowNavi": "null",
            "str_NaviCSS": "null",
            "str_ColbgCSS": "null",
            "str_NaviPic": "null",
            "str_PageStyle": "0$$22$plist"
        }
        r = self.http.request("POST","http://news.ncu.edu.cn/frontDialogClassNewsList_getClassNews?no-cache=0.8513723373442865",fields=ncu_postfields)
        while int(r.status)!=200:
            time.sleep(10)
            r = self.http.request("POST", "http://news.ncu.edu.cn/frontDialogClassNewsList_getClassNews?no-cache=0.8513723373442865",fields=ncu_postfields)
        res = []
        for m in re.split("</li>",r.data.decode("utf-8")):
            #print(m)
            start = m.find("/html")
            #print(start)
            end = m.find(".html\"")  + 5
            start_date = m.find("\"date\"")
            end_date = m.find("\"views\"")
            m_view = m[end_date:]
            #print(m_view)
            start_view = end_date
            end_view = m_view.find("</span>")
            #print(start_view)
            if len(m[start:end])==0:
                break
            res.append({"url":m[start:end],"date":m[start_date+7:end_date-19],"view":m_view[8:end_view]})
        return res

    def parse_cfau(self,page):
        print("----------------"+str(page)+"------------------")
        start = 60*(page-1)+1
        end = 60*page
        r = self.http.request("POST","http://www.cfau.edu.cn/module/web/jpage/dataproxy.jsp?startrecord="+str(start)+"&endrecord="+str(end)+"&perpage=60&col=1&appid=1&webid=27&path=%2F&columnid=2983&sourceContentType=1&unitid=9495&webname=%E5%A4%96%E4%BA%A4%E5%AD%A6%E9%99%A2&permissiontype=0")
        while int(r.status)!=200:
            time.sleep(10)
            r = self.http.request("POST","http://www.cfau.edu.cn/module/web/jpage/dataproxy.jsp?startrecord="+str(start)+"&endrecord="+str(end)+"&perpage=60&col=1&appid=1&webid=27&path=%2F&columnid=2983&sourceContentType=1&unitid=9495&webname=%E5%A4%96%E4%BA%A4%E5%AD%A6%E9%99%A2&permissiontype=0")
        htmldoc = r.data.decode("utf-8")
        print(htmldoc)
        res = []
        datastore_start = htmldoc.find("<recordset>")
        datastore_end = htmldoc.find("</recordset>")
        datastore_doc = htmldoc[datastore_start:datastore_end]
        for m in re.split("</li>", datastore_doc):
            start_url = m.find("href=")
            end_url = m.find("target=")
            start_date = m.find("right")
            end_date = m.find("</span>")
            if len(m[start_url+6:end_url-1].replace("\"",""))==0:
                break
            res.append({"url": m[start_url+6:end_url-1].replace("\"",""), "date": m[start_date+8:end_date]})
        print(res)
        return res











