from google_patents_1.google_carwlers.google_crawlers import GoogleCrawlers
from google_patents_1.utils.utils import init

if __name__ == '__main__':
    mysql_pool, config, pub_ids = init("config.ini")
    GoogleCrawlers(mysql_pool, config, pub_ids).start()
    mysql_pool.close_all_connections()