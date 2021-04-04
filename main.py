import shutil
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from Exception.CustomException import *
from decimal import Decimal
from api.Saucenao import *
from utils import logger
from utils import utils
from utils.similarity import ImageCompare


find_path = os.path.join(os.path.abspath('.'), 'resources')
search = Saucenao()
for root, dirs, files in os.walk(find_path):
    dirs[:] = [d for d in dirs if os.path.isdir(d)]
    for file in files:
        filename = os.path.join(root, file)
        if utils.is_image(filename):
            logger.info("Search illustration: " + file)
            # illust = search.search_by_api()
            try:
                illust = search.search_by_normal(filename)
            except OutOfSearch:
                sys.exit(0)
            if not illust:
                shutil.move(filename, os.path.join(root, 'NotFound'))
                continue
            if not utils.verify(illust.illust_id,illust.illust_title):
                logger.warn("The illustration have been searched")
                shutil.move(filename, os.path.join(root, 'Backups'))
                continue
            if Decimal(illust.similarity) > 80:
                try:
                    download_results = utils.download_image(illust, filename)
                except:
                    logger.error("Illustration doesn't match")
                if download_results:
                    utils.write_to_redis(illust.illust_id,illust.illust_title)
                    shutil.move(filename, os.path.join(root, 'Backups'))
                else:
                    shutil.move(filename, os.path.join(root, 'Invalid'))
            else:
                logger.fail("Similarity is too low,skip this illustration")
                shutil.move(filename, os.path.join(root, 'NotFound'))
            logger.info("Search complete,sleep 10s")
            time.sleep(10)
logger.info("All illustration finished")
