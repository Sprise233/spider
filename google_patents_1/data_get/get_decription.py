import re

from bs4 import BeautifulSoup

from google_patents_1.data_get.get_basic_data import BasicData
from google_patents_1.utils.utils import log, init, subset


class DecriptionData:
    def __init__(self, mysql_connection, config, pub_num):
        self.mysql_connection = mysql_connection
        self.config = config
        self.pub_num = pub_num
        self.html = ""

    def search(self, html):
        self.html = html
        try:
            self.__getData()
            self.__saveData()
        except:
            log("获取描述信息错误-------------------------------------------------------------------------------！！！")

    def __getData(self):
        fig_list = []

        soup = BeautifulSoup(self.html, 'html.parser')

        # 获取所有div块中的内容
        pattern_class = re.compile(r'description')
        pattern_num = re.compile(r'\d')
        div_list = soup.find_all('div', class_=pattern_class, num=pattern_num)

        # 获取div块中有fig字符的内容
        div_fig_list = []
        for div in div_list:
            div_text = div.text.strip()
            pattern = r'^(FIGS?). \d+'

            # 获得图片的描述
            match = re.search(pattern, div_text)

            if match:
                div_fig_list.append(div_text)

        # for i, div in enumerate(div_fig_list):
        #     print(str(i)+"----"+div)

        # fig描述的内容
        div_fig_list = []
        return None

    def __saveData(self):
        return None



if __name__ == '__main__':

    pub_num = "US7786877B2"

    mysql_connection, config, pub_ids = init("../config.ini", pub_ids_url="../data/keys.csv")
    basicData = BasicData(mysql_connection, config, pub_num)
    decriptionData = DecriptionData(mysql_connection, config, pub_num)
    html = basicData.search()
    decriptionData.search(html)

