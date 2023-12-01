# https://patents.google.com/patent/US20080002423A1/en?oq=US20080002423A1
import re
import time

import requests
from bs4 import BeautifulSoup

from google_patents_1.utils.utils import init
from google_patents_1.utils.utils import log
class BasicData:
    '''
    每一个类只爬取一个专利的基本内容
    '''
    def __init__(self, mysql_connection, config, pub_num):
        self.mysql_connection = mysql_connection
        self.config = config
        self.pub_num = pub_num
        self.html = ""
        # 图像地址信息
        '''
        image_ids   :   图像的唯一标识:公共号+图片号
        image_urls  :   图像地址信息
        '''
        self.data = {}

    def search(self):
        # imageId_imageUrl = self.__getData()
        self.__getData()
        self.__saveData()
        # return imageId_imageUrl
        return self.html

    def __getData(self):
        data = {}
        pub_num = self.pub_num
        try:
            data['html'] = self.__get_patent_html()
        except:
            # print(f"专利号<--{pub_num}-->未找到专利信息")
            log(f"专利号<--{pub_num}-->未找到专利信息")
        return data

    def __get_patent_html(self):
        pub_num = self.pub_num

        url = "https://patents.google.com/patent/" + str(pub_num) + "/en?oq=" + str(pub_num)
        # 获取专利的html
        resp = requests.get(url, headers=self.config['headers'], proxies=self.config['proxies'])
        resp.encoding = 'utf-8'
        html = resp.text
        self.html = html



    def __saveData(self):
        return None



if __name__ == '__main__':
    mysql_connection, config, pub_ids = init("D:\python_code\spider\google_patents\config.ini")
    baseData = BasicData(mysql_connection, config, pub_ids)
    baseData.search("US20080002423A1")
