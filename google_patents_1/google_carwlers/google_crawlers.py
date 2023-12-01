import threading
import time
from concurrent.futures import ThreadPoolExecutor
from google_patents_1.data_get.get_basic_data import BasicData
from google_patents_1.data_get.get_image import ImageData
from google_patents_1.data_get.get_decription import DecriptionData
from google_patents_1.utils.utils import log


class GoogleCrawlers():
    def __init__(self, mysql_pool, config, pub_ids):
        self.mysql_pool, self.config, self.pub_ids = mysql_pool, config, pub_ids
        self.headers_list = []
        # 用来选择使用哪个头
        self.i = 0
        # 给公共资源i上锁
        self.lock = threading.Lock()

        # 第几个已经完成了,虽然线程不安全，但是仅仅是一个指示器，不需要安全
        self.num = 0
    def google_clawler(self, pub_num):

        time.sleep(1)
        # with self.lock:
        #     if self.i == len(self.headers_list):
        #         self.i = 0
        #     else:
        #         self.i += 1
        headers = self.headers_list[self.i]
        mysql_connection, config, pub_ids = self.mysql_pool.get_connection(), self.config, self.pub_ids

        config['headers'] = headers
        # print(config)
        # 获取基础数据
        basicData = BasicData(mysql_connection, config, pub_num)
        # 获取图像数据
        imageData = ImageData(mysql_connection, config, pub_num)
        # 获取描述数据
        # decriptionData = DecriptionData(mysql_pool, config, pub_num)

        html = basicData.search()
        imageData.search(html)
        # decriptionData.search(html)

        log(f"第<--{self.num}/{len(pub_ids)}-->专利号<--{pub_num}-->信息获取完成")
        self.num+=1

        self.mysql_pool.release_connection(mysql_connection)

    def get_header_list(self):
        headers_list = []
        headers_list.append(self.config['headers1'])
        headers_list.append(self.config['headers2'])
        headers_list.append(self.config['headers3'])
        headers_list.append(self.config['headers4'])
        headers_list.append(self.config['headers5'])
        headers_list.append(self.config['headers6'])
        headers_list.append(self.config['headers7'])
        headers_list.append(self.config['headers8'])
        headers_list.append(self.config['headers9'])
        headers_list.append(self.config['headers10'])
        headers_list.append(self.config['headers11'])
        headers_list.append(self.config['headers12'])
        headers_list.append(self.config['headers13'])
        headers_list.append(self.config['headers14'])
        headers_list.append(self.config['headers15'])
        headers_list.append(self.config['headers16'])
        headers_list.append(self.config['headers17'])
        headers_list.append(self.config['headers18'])
        headers_list.append(self.config['headers19'])
        headers_list.append(self.config['headers20'])
        self.headers_list = headers_list

    def start(self):
        self.get_header_list()
        # 创建线程池，设置最大线程数在配置文件中
        max_threads = int(self.config['mysql_connect']['size'])
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # 提交每个URL的爬取任务给线程池
            # 此处使用submit方法，每个任务为crawl_url函数，参数为urls中的一个URL
            executor.map(self.google_clawler, self.pub_ids)
