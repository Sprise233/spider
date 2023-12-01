# https://patents.google.com/patent/US20080002423A1/en?oq=US20080002423A1
# https://patentimages.storage.googleapis.com/36/d5/96/3af7a85c1c39b1/US20080002423A1-20080103-D00002.png
# url = "https://patents.google.com/patent/US20080002423A1/en?oq=US20080002423A1
import re
import threading
import time

import requests
from PIL import Image
from bs4 import BeautifulSoup

from google_patents.utils.utils import log
class ImageData:
    def __init__(self, mysql_connection, config, pub_num):
        self.mysql_connection = mysql_connection
        self.config = config
        self.pub_num = pub_num
        self.html = ""
        '''
        image_ids   :   图像的唯一标识:公共号+图片号
        image_urls  :   图像地址信息
        '''
        self.data = {}

        self.lock = threading.Lock()

    def search(self, html):
        self.html = html

        self.__getData()
        self.__saveData()

    def __getData(self):
        try:
            image_urls = self.__get_image_url()
            self.data['image_urls'] = image_urls
        except:
            # print(f"专利号<--{pub_num}-->图像信息寻找失败")
            log(f"专利号<--{self.pub_num}-->图像信息寻找失败")

        try:
            image_ids = self.__get_image_url()
            self.data['image_ids'] = image_ids
        except:
            # print(f"专利号<--{pub_num}-->图像id编码失败")
            log(f"专利号<--{self.pub_num}-->图像id编码失败")

    def __get_image_url(self):

        image_urls = []
        '''
        :param pub_num: 专利号
        :return:图片网址列表
        '''

        # 找到这样的网址
        # < meta itemprop = "full" content = "https://patentimages.storage.googleapis.com/36/d5/96/3af7a85c1c39b1/US20080002423A1-20080103-D00002.png" >

        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(self.html, 'html.parser')

        meta_list = soup.find_all('meta', itemprop='full')
        # re解析
        for meta in meta_list:
            re_string = '<meta content="(?P<image_url>.*?)" itemprop="full"/>'
            obj = re.compile(re_string, re.S)
            image_urls.append(obj.search(meta.prettify()).group('image_url'))

        return image_urls

    def __get_image_ids(self):
        '''
        获取专利的额标号
        :return:
        '''

        image_ids = []

        image_urls = self.data['image_urls']
        for i in len(image_urls):
            image_id = str(self.pub_num) + '-{:08d}'.format(i)
            image_ids.append(image_id)

        self.data['image_ids'] = image_ids

    def __get_image_data(self, url):
        resp = requests.get(url, headers=self.config['headers'], proxies=self.config['proxies'])
        return resp.content

    def __saveData(self):
        pub_num = self.pub_num

        try:
            self.__save_image_message_to_images()
        except Exception as e:
            # print(f"专利号<--{pub_num}-->保存image_id和image_url到images表中失败")
            log(f"专利号<--{pub_num}-->获取mysql连接失败"+"问题为："+str(e))

    def __save_image_message_to_images(self):
        cursor = self.mysql_connection.cursor()
        image_id = ""
        image_url = ""
        try:
            # 开始事务
            self.mysql_connection.start_transaction()
            for i, image_url in enumerate(self.data['image_urls']):
                image_id = str(self.pub_num) + '_{:08d}'.format(i)
                image_data = self.__get_image_data(image_url)
                # # 执行查询,看看是否已经有了这个关键字，如果有了，那么就不进行查询了
                # query = "SELECT * FROM images WHERE image_id = %s"
                # cursor.execute(query, (image_id,))
                #
                # # 获取查询结果
                # result = cursor.fetchall()
                #
                # # 检查结果是否存在
                # if result:
                #     log(f"图片 '{image_id}' 已经存在于数据库中了。")
                #     continue
                # print(image_id)
                insert_query = "INSERT INTO images (image_id, image_data, image_url) VALUES (%s, %s, %s)"
                # 执行插入操作
                cursor.execute(insert_query, (image_id, image_data, image_url))
                # 提交更改
                self.mysql_connection.commit()

        except:

            log(f"图片内容操作失败！！！专利号<--{self.pub_num}-->的图片<--{image_id}-->图片的url为：<--{image_url}-->插入信息到images表中失败")
                # 发生异常时回滚事务
            self.mysql_connection.rollback()
        finally:
            cursor.close()