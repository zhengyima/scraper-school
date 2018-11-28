#coding:utf-8
import time
from selenium import webdriver
from pyvirtualdisplay import Display
display=Display(visible=0,size=(800,800))
display.start()
driver=webdriver.Firefox(log_path='/home/dou/gd2.log')
driver.get('http://www.cnblogs.com/')
time.sleep(5)
title=driver.title
print(title.encode('utf-8'))
driver.close()
display.stop()
