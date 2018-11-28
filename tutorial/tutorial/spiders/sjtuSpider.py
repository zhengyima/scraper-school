import scrapy

from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from scrapy_splash import SplashRequest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display
import traceback

class sjtuSpider(scrapy.Spider):
    name = "sjtu"

    def __init__(self, category=None, *args, **kwargs):
        super(sjtuSpider, self).__init__(*args, **kwargs)

        display = Display(visible=0, size=(800, 600))
        display.start()

        self.driver = webdriver.Chrome()
        self.driver.set_page_load_timeout(10)


    def start_requests(self):
        urls = [
            'http://news.nju.edu.cn/mtjj.html'
        ]
        for url in urls:
            yield SplashRequest(url, self.parse,args={'wait': 0.5})

    def parse(self,response):
        url_set = set()  # 话题url的集合

        print(response.url)
        print(response.css("a#next").extract_first())
        self.driver.get(response.url)

        url_sum_lists = []
        while True:
            try:
                wait = WebDriverWait(self.driver, 10)
            #wait.until(lambda driver: driver.find_element_by_xpath('//div[@class="content"]/ul/li/a'))
                wait.until(lambda driver: driver.find_element_by_xpath('//li[@class="t"]/a'))
            except:
                pass

            sel_list = self.driver.find_elements_by_xpath('//li[@class="t"]/a')

            url_list = []
            for sel in sel_list:
                try:
                    url_list.append(sel.get_attribute("href"))
                except:
                    continue

            #url_list = [sel for sel in sel_list]
            url_sum_lists += url_list
            url_set |= set(url_list)

            print(len(url_set))



            try:
                wait = WebDriverWait(self.driver, 10)
                wait.until(lambda driver: driver.find_element_by_xpath("//a[@id='next']"))
                next_page = self.driver.find_element_by_xpath("//a[@id='next']")
                #print("@#@@#@!#!#!#"+next_page.get_attribute('href'))
                #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n\n\n")
                #print(next_page)
                if(int(next_page.get_attribute('pn')) == 201):
                    break
                self.driver.execute_script("arguments[0].click();", next_page)

                #next_page.click()  # 模拟点击下一页
            except Exception as e :
                traceback.print_exc()
                info = traceback.format_exc()
                print("#####Arrive thelast page.#####")
                break

            #for url in url_sum_lists:
                #print(url)
            #print("\n\n\nlen:"+str(len(url_set)))

        print("len of sum is :"+str(len(url_sum_lists)))
        for url in url_sum_lists:
            print(url)

        #print("".join(response.css(".next").extract()))
        #yield response.css(".next").extract_first()
        #yield response.css(".whj_border").extract_first()
    def parse_news(self,response):
        yield {"title":response.css(".article_title").extract_first()}

