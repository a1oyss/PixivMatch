import shutil
import sys
from decimal import Decimal
from api.Saucenao import *
from utils import logger
from utils import utils


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
                continue
            file_hash = utils.get_hash(filename)
            if not utils.verify(file_hash):
                logger.warn("The illustration have done searched")
                continue
            if Decimal(illust.similarity) > 80:
                download_results = utils.download_image(illust)
                if download_results:
                    utils.write_to_csv(file_hash)
                    shutil.move(filename, os.path.join(root, 'Backups'))
                else:
                    shutil.move(filename, os.path.join(root, 'Invalid'))
            else:
                logger.fail("Similarity is too low,skip this illustration")
                shutil.move(filename, os.path.join(root, 'NotFound'))
            logger.info("Search complete,sleep 10s")
            time.sleep(10)
logger.info("All illustration finished")
