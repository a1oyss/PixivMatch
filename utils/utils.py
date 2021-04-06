import redis
from Exception.CustomException import NotSame
from configparser import ConfigParser
from operator import itemgetter
from utils import redisConn
import cv2
import numpy as np
from bean.illust import Illust
from PIL import Image
from bean.config import Config
from bs4 import BeautifulSoup
from utils import logger
from html import unescape
from tqdm import tqdm
from utils import similarity
import matplotlib.pyplot as plt
import hashlib
import os
import io
import re
import requests
import json
import csv


def read_config():
    """
    读取配置文件
    :return: 返回Config对象
    """
    config_path = os.path.join(os.path.abspath('.'), 'config.ini')
    config = ConfigParser()
    config.read(config_path, encoding='utf-8')
    api_key = config.get('api', 'api_key')
    minsim = config.get('api', 'minsim')
    db = config.items('db')
    db_bitmask = ''.join([value for name, value in db])
    return Config(api_key, minsim, int(db_bitmask, 2))


def image_read(filename):
    """
    读取图片，保存到内存中
    :param filename: 图片路径
    :return: 返回图片数据
    """
    image = Image.open(filename)
    image = image.convert('RGB')
    image.thumbnail((250, 250), resample=Image.ANTIALIAS)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_data = image_bytes.getvalue()
    image_bytes.close()
    return image_data


def parse_content(content):
    """
    解析html，获取Illust对象
    :param content: 要解析的数据
    :return: 返回Illust对象
    """
    soup = BeautifulSoup(content, 'html5lib')
    results_list = soup.find_all('div', 'result')
    pixiv_list = []
    for i in results_list:
        results_dict = {}
        match_str = str(i)
        try:
            results_dict['similarity'] = re.search(
                r'<div class="resultsimilarityinfo">(.*?)%</div>', match_str).group(1)
            results_dict['illust_id'] = re.search(
                r'illust_id=(\d+)"', match_str).group(1)
            results_dict['illust_url'] = "https://www.pixiv.net/artworks/" + \
                                         results_dict['illust_id']
            results_dict['illust_title'] = re.search(
                r'<div class="resulttitle"><strong>(.*?)</strong>', match_str).group(1)
            results_dict['member_id'], results_dict['member_name'] = re.findall(
                r'member\.php\?id=(\d+)">(.*?)</a>', match_str)[0]
            pixiv_list.append(results_dict)
        except:
            continue
    if pixiv_list:
        results = max(pixiv_list, key=itemgetter('similarity'))
    else:
        return 0
    return Illust(results['similarity'], results['illust_id'], results['illust_url'], results['illust_title'],
                  results['member_id'], results['member_name'])


def download_image(illust, original):
    """
    下载图片
    :param illust: Illust对象
    :return: 下载成功返回图片路径，失败返回None
    """
    headers = {
        'Referer': 'https://www.pixiv.net/'
    }
    r = requests.get(illust.illust_url)
    # print(r.encoding)
    if r.status_code == 404:
        logger.warn("The source of the image was removed")
        return None
    soup = BeautifulSoup(r.content, 'html5lib', from_encoding='utf-8')
    # print(soup.original_encoding)
    meta = soup.find(attrs={'name': 'preload-data'})
    #content = json.JSONDecoder().decode(meta['content'])
    content = json.loads(meta['content'])
    # 原图链接
    original_image = content['illust'][illust.illust_id]['urls']['original']
    # 扩展名
    ext_name = original_image[-4:]
    # 页数
    page_count = content['illust'][illust.illust_id]['userIllusts'][illust.illust_id]['pageCount']
    # 收藏数
    bookmark_count = content['illust'][illust.illust_id]['bookmarkCount']
    # 作者名称
    member_name = content['user'][illust.member_id]['name']
    # 插图标题
    illust_title = content['illust'][illust.illust_id]['illustTitle']
    # 图片保存目录
    base_path = make_dir(member_name, illust.member_id)
    download_list = []
    for i in range(page_count):
        save_name = str(bookmark_count) + "_" + \
            filter_name(illust_title) + '_' + str(i) + ext_name
        save_path = os.path.join(base_path, save_name)
        r = requests.get(re.sub(r'_p(\d)', '_p' + str(i),
                                original_image), headers=headers)
        if r.headers.get('Content-Length'):
            image_size = int(r.headers['Content-Length'], 0)
            logger.info("Start download illustration...")
            with open(save_path, 'wb') as file, tqdm(desc=illust_title+'_'+str(i), total=image_size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for data in r.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)
            logger.success("Download illustration " + filter_name(illust_title) +
                           '_'+str(i) + " complete! Saved in " + base_path)
            download_list.append(save_path)
        else:
            logger.warn("Transfer-Encoding: Chunked")
            with open(save_path, 'wb') as file:
                file.write(r.content)
            logger.success("Download illustration " + filter_name(illust_title) +
                           '_'+str(i) + " complete! Saved in " + base_path)
            download_list.append(save_path)
    logger.info("Download complete,compare image...")
    is_same = compare(download_list, original, False)
    if not is_same:
        raise NotSame
    return is_same


def make_dir(author, author_id):
    """
    创建图片目录
    :param author: 作者name
    :param author_id: 作者id
    :return: 创建好的路径
    """
    resources_dir = os.path.join(os.path.abspath('.'), 'resources')
    author_dir = author_id + '_' + filter_name(unescape(author))
    final_path = os.path.join(resources_dir, author_dir)
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    return final_path


def filter_name(name):
    """
    过滤Windows敏感字符
    :param name: 要过滤的字符串
    :return: 返回合格字符串
    """
    filter_list = {r'\/': '／', r'\\': '＼',
                   r'\:': '：', r'\*': '＊',
                   r'\?': '？', r'"': '＂',
                   r'\<': '＜', r'\>': '＞',
                   r'\|': '｜', r'\.': '．'}
    new_name = name
    for i in filter_list.items():
        new_name = re.sub(i[0], i[1], new_name)
    return new_name


def get_hash(filename):
    """
    计算文件hash值
    :param filename: 文件路径
    :return: 返回hash值
    """
    _hash = hashlib.md5()
    with open(filename, 'rb') as file:
        _hash.update(file.read())
    return _hash.hexdigest()


def write_to_redis(pid,title):
    """
    将pid写入csv文件
    :param value: 要写入的pid
    :return: None
    """
    r=redisConn.Redis()
    r.hset('setu:pixiv', pid, title)


def verify(pid,title):
    """
    验证下载图片是否相同
    :param pid:
    :return: 不存在返回True，否则返回False
    """
    r=redisConn.Redis()
    if r.hexists('setu:pixiv', pid):
        return False
    return True 


def is_image(filename):
    """
    检测文件是否是图片
    :param filename: 文件名
    :return: 
    """
    extensions = ["jpg", "jpeg", "png", "gif", "bmp", "jfif"]
    ext = filename.split('.')[-1]
    if ext in extensions:
        return True
    return False


def compare(path_list, original_path, show=False):
    illust_compare = similarity.ImageCompare()
    flag = False
    if show:
        plt.ion()
        original = cv2.imdecode(np.fromfile(
            original_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        plt.subplot(1, 2, 1).set_title('original')
        plt.imshow(original)
        for file in path_list:
            image = cv2.imdecode(np.fromfile(
                file, dtype=np.uint8), cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            plt.subplot(1, 2, 2).set_title('diff')
            plt.tight_layout()
            plt.imshow(image)
            if illust_compare.dHash_compare(original_path, file) > 90:
                flag = True
            plt.show()
            plt.pause(2)
            plt.cla()
    else:
        for file in path_list:
            if illust_compare.dHash_compare(original_path, file) > 90:
                flag = True
    if flag:
        return True
    else:
        return False
