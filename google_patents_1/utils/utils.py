import configparser
import csv
import io
import re
import threading
import time

import requests
from PIL import Image
from mysql.connector import Error
from datetime import datetime

import mysql.connector


# def getconnect(config):
#
#     '''
#     当前不使用 selenium
#     :param config:
#     :return:
#     '''
#
#     # chrome_options = Options()
#     # # 指定驱动程序的路径
#     # driver_path = config['chrome_connect']['driver_path']
#     #
#     # pid = config['chrome_connect']['pid']
#     # # 设置Chrome启动参数
#     # chrome_options = webdriver.ChromeOptions()
#     # chrome_options.add_argument('--remote-debugging-port=' + str(pid))
#     # # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9527")  # 通过端口号接管已打开的浏览器
#     # chrome_connection = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
#     # chrome_connection.get(config['chrome_connect']['url'])
#     # # chrome_connection.delete_all_cookies()
#     # chrome_connection.implicitly_wait(120)
#
#     # 创建mysql连接
#     mysql_connection = mysql.connector.connect(
#         host=config['mysql_connect']['host'],
#         port=config['mysql_connect']['port'],
#         database=config['mysql_connect']['database'],
#         user=config['mysql_connect']['user'],
#         password=config['mysql_connect']['password']
#     )
#
#
#     # return chrome_connection, mysql_connection
#     return mysql_connection

# 创建一个线程安全的数据库连接池
# class MySQLConnectionPool:
#     def __init__(self, config):
#         self.config = config
#         self.size = int(config['mysql_connect']['size'])
#         self.pool = [self.create_connection() for _ in range(self.size)]
#         self.lock = threading.Lock()
#
#     def create_connection(self):
#         return mysql.connector.connect(
#             host=self.config['mysql_connect']['host'],
#             port=self.config['mysql_connect']['port'],
#             database=self.config['mysql_connect']['database'],
#             user=self.config['mysql_connect']['user'],
#             password=self.config['mysql_connect']['password']
#         )
#
#     def get_connection(self):
#         with self.lock:
#             return self.pool.pop()
#
#     def release_connection(self, connection):
#         with self.lock:
#             self.pool.append(connection)
#
#     def close_all_connections(self):
#         with self.lock:
#             while not self.connection_pool.empty():
#                 connection = self.connection_pool.get()
#                 connection.close()

# # mysql连接池二版
# import mysql.connector
# import queue
# import threading
#
# class MySQLConnectionPool:
#     def __init__(self, config):
#         self.config = config
#         self.db_config = {
#             # 'host': host,
#             # 'user': user,
#             # 'password': password,
#             # 'database': database,
#             'host'      : self.config['mysql_connect']['host'],
#             'port'      : self.config['mysql_connect']['port'],
#             'user'      : self.config['mysql_connect']['user'],
#             'password'  : self.config['mysql_connect']['password'],
#             'database'  : self.config['mysql_connect']['database'],
#         }
#         self.pool_size = int(config['mysql_connect']['size'])
#         self.connection_pool = queue.Queue()
#         self.lock = threading.Lock()
#
#     def create_connection(self):
#         return mysql.connector.connect(**self.db_config)
#
#     def get_connection(self):
#         with self.lock:
#             if not self.connection_pool.full():
#                 # Check again inside the lock to avoid race condition
#                 if not self.connection_pool.full():
#                     connection = self.create_connection()
#                     self.connection_pool.put(connection)
#             print("-拿取线程池------------" + str(self.connection_pool.qsize()))
#             return self.connection_pool.get()
#
#     def release_connection(self, connection):
#         with self.lock:
#             self.connection_pool.put(connection)
#             print("退回线程池------------" + str(self.connection_pool.qsize()))
#
#     def close_all_connections(self):
#         with self.lock:
#             while not self.connection_pool.empty():
#                 connection = self.connection_pool.get()
#                 connection.close()

import mysql.connector
import queue
import threading

class MySQLConnectionPool:
    def __init__(self, config):
        self.db_config = {
            'host'      : config['mysql_connect']['host'],
            'port'      : config['mysql_connect']['port'],
            'user'      : config['mysql_connect']['user'],
            'password'  : config['mysql_connect']['password'],
            'database'  : config['mysql_connect']['database'],
        }
        self.pool_size = int(config['mysql_connect']['size'])
        self.connection_pool = queue.Queue(maxsize=self.pool_size)
        self.lock = threading.Lock()

        # 创建连接并填充连接池
        with self.lock:
            for _ in range(self.pool_size):
                connection = self.create_connection()
                self.connection_pool.put(connection)

    def create_connection(self):
        return mysql.connector.connect(**self.db_config)

    def get_connection(self):
        with self.lock:
            print("-拿取线程池之前------------" + str(self.connection_pool.qsize()))
            return self.connection_pool.get()

    def release_connection(self, connection):
        print("-释放线程池之前------------" + str(self.connection_pool.qsize()))
        self.connection_pool.put(connection)

    def close_all_connections(self):
        with self.lock:
            while not self.connection_pool.empty():
                connection = self.connection_pool.get()
                connection.close()







def getconfig(url):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(url, encoding='utf-8')

    # 将配置内容转换为字典
    config_dict = {}
    print("----------读取配置信息---------")
    for section in config.sections():
        config_dict[section] = {}
        if "headers" not in section:
            print("--------Section:\t" + section + "--------")
        for option in config.options(section):
            config_dict[section][option] = config.get(section, option)
            if "headers" not in section:
                print(option + ":\t" + config_dict[section][option])

    return config_dict


def init(url, pub_ids_url=""):
    config = getconfig(url)

    if pub_ids_url=="":
        pub_ids_url = config['search']['pub_ids_url']
    # print(pub_ids_url)
    # 打开原始 CSV 文件并读取数据
    with open(pub_ids_url, 'r', encoding='utf-8') as input_file:
        reader = csv.DictReader(input_file)
        pub_ids = [row['pub_id'] for row in reader]  # 获取指定列的数据

    # chrome_connection, mysql_connection = getconnect(config)
    # return chrome_connection, mysql_connection, config, pub_ids
    # mysql_connection = getconnect(config)
    mysql_connection = MySQLConnectionPool(config)
    return mysql_connection, config, pub_ids

# 将二进制字符串转化为图片对象
def binary_string_to_image(binary_string):
    # 将二进制字符串转换为字节流
    byte_stream = io.BytesIO(binary_string)

    # 使用PIL库读取字节流为图像
    image = Image.open(byte_stream)

    # 返回图像对象，你可以在此进行后续处理，比如保存为文件
    return image


# 将图片对象转化为gif文件
def save_image_as_gif(image, file_path):
    # 使用PIL库的save方法将图像保存为GIF文件
    image.save(file_path, format='GIF')



import mysql.connector

# 删除数据库中某个表的所有行
def delete_all_rows_from_table(mysql_connection, table_name):
    with mysql_connection.cursor() as cursor:
        sql = f"DELETE FROM {table_name}"

        cursor.execute(sql)
    mysql_connection.commit()

# 写日志文件
def log(text, top=""):
    # 获取当前时间
    current_time = datetime.now()

    # 将时间格式化为指定格式（包含年、月、日、小时、分钟、秒）
    formatted_time = current_time.strftime("%Y-%m-%d-%H-%M-%S")

    with open("log.txt", 'a', encoding='utf-8') as file:
        file.write(top+formatted_time+"---"+text+"\n")

# 判断一个字符串是否是另一个字符串的子集,如果是子集,那么将子集并入全集中
def subset(str1, str2):
    '''
    :param str1:字符串
    :param str2:字符串
    :return:输出全集，不是子集关系输出为空
    '''
    set1 = set(str1)
    set2 = set(str2)

    if set1.issubset(set2):
        return set2
    elif set2.issubset(set1):
        return set1
    else:
        return None

import spacy

# def get_subject(text):
#     # 加载英语语言模型
#     nlp = spacy.load("en_core_web_sm")
#
#     # 处理文本
#     text = "Your input sentence goes here. It can contain multiple sentences."
#
#     # 使用 SpaCy 处理文本
#     doc = nlp(text)
#
#     # 打印每个词的依存关系和头部词（head）
#     for token in doc:
#         print(f"{token.text}: {token.dep_}, {token.head.text}")
#
#     # 获取主语
#     subjects = [token.text for token in doc if "subj" in token.dep_]
#     print(f"主语：{subjects}")

def get_subject(text):
    # 目前是使用正则表达式匹配,未来想使用ai
    pattern = r'FIGS\. \d+[A-Za-z]*(?:˜\d+[A-Za-z]*)*'

if __name__ == '__main__':
    mysql_connection, config, pub_ids = init("../config.ini", pub_ids_url='../data/keys.csv')
    yes_or_no = input("是否删除？yes_or_no?")
    if yes_or_no=="yes":
        delete_all_rows_from_table(mysql_connection.get_connection(), 'images')
    # print(getDecription("USD0873357S", config))
    # save_image_as_gif(binary_string_to_image(), "test.gif")



