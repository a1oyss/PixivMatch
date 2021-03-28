import time
from bean.illust import Illust
from utils import utils
from utils import logger
from Exception.CustomException import *
from collections import OrderedDict
import requests
import json
import os


class Saucenao(object):
    def __init__(self):
        """初始化配置
        """
        config = utils.read_config()
        self.api_key = config.api_key
        self.minsim = config.minsim
        self.db_bitmask = config.db_bitmask

    def search_by_api(self, filename):
        """使用API搜索

        Parameters
        ----------
        filename : str
            图片路径

        Returns
        -------
        Illust
            Illust对象

        Raises
        ------
        ServiceError
            服务器错误
        APIError
            API配置错误
        RequestError
            请求错误
        IndexError
            Index配置错误
        OutOfSearch
            超出查询次数
        TooQuick
            查询过快
        """
        image_data = utils.image_read(filename=filename)
        url = 'http://saucenao.com/search.php?output_type=2&numres=1&minsim=' + \
              self.minsim + '&dbmask=' + str(self.db_bitmask) + '&api_key=' + self.api_key
        files = {'file': ("image.png", image_data)}
        process_results = False
        while True:
            session = requests.session()
            session.keep_alive = False
            try:
                r = session.post(url=url, files=files)
            except:
                logger.warn("Connection failed,retrying after 5s...")
                time.sleep(5)
                continue
            if r.status_code != 200:
                if r.status_code == 403:
                    logger.error("403 Forbidden,Service Error")
                    raise ServiceError
                else:
                    logger.info("Status code: " + str(r.status_code) + ",Retrying...")
            else:
                results = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(r.text)
                # user id 正确
                if int(results['header']['user_id']) > 0:
                    logger.info('Remaining Searches 30s|24h: ' +
                                str(results['header']['short_remaining']) + '|' + str(
                        results['header']['long_remaining']))
                    if int(results['header']['status']) == 0:
                        # search succeeded for all indexes, results usable
                        process_results = True
                        logger.info("Search Complete")
                        break
                    else:
                        if int(results['header']['header']) > 0:
                            logger.error("API Error,Please check config...")
                            raise APIError
                        else:
                            logger.error("Bad image or other request error.Please check image: " + filename)
                            raise RequestError
                else:
                    raise RequestError
        if process_results:
            if int(results['header']['results_returned']) > 0:
                if float(results['results'][0]['header']['similarity']) > 80:
                    logger.success('Hit! ' + str(results['results'][0]['header']['similarity']))
                    # service_name='' # 图床网站
                    # similarity=0    # 相似度
                    # illust_url=''   # 作品地址
                    # illust_title=''        # 作品标题
                    # illust_id=''    # 作品id
                    # member_name=''  # 作品作者
                    # member_id=''    # 作品作者id
                    index_id = results['results'][0]['header']['index_id']
                    if index_id == 5 or index_id == 6:
                        service_name = 'pixiv'
                        similarity = results['results'][0]['header']['similarity']
                        illust_url = results['results'][0]['data']['ext_urls']
                        illust_title = results['results'][0]['data']['title']
                        illust_id = results['results'][0]['data']['pixiv_id']
                        member_name = results['results'][0]['data']['member_name']
                        member_id = results['results'][0]['data']['member_id']
                    else:
                        # unknown
                        logger.error("Index Error,Please check config")
                        raise IndexError
            else:
                logger.fail('No results...')
                return None
            if int(results['header']['long_remaining']) < 1:
                logger.error("You have reached the daily limit,Change IP and continue")
                raise OutOfSearch
            if int(results['header']['short_remaining']) < 1:
                logger.error("Too quickly,sleep a little time")
                raise TooQuick
        return Illust(similarity, illust_url[0], illust_title, illust_id, member_name, member_id)

    def search_by_normal(self, filename):
        """不使用API查询

        Parameters
        ----------
        filename : str
            文件名

        Returns
        -------
        Illust
            成功返回Illust对象，失败返回None
        """
        image_data = utils.image_read(filename)
        url = 'https://saucenao.com/search.php'
        files = {'file': ("image.png", image_data)}
        session = requests.session()
        session.keep_alive = False
        while True:
            try:
                r = session.post(url=url, files=files)
            except:
                logger.warn("Connection failed,retrying after 5s...")
                time.sleep(5)
                continue
            if "Limit" in r.text:
                logger.error("You have reached the daily limit,Change IP and press Enter to continue")
                os.system('pause')
                continue
            illust = utils.parse_content(r.content)
            if not illust:
                logger.fail("No results...")
                return None
            logger.success("Hit! " + illust.similarity)
            return illust
