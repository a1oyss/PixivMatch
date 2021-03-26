import logging
import colorlog

# logger配置
LOG_LEVEL = logging.DEBUG
LOG_FORMAT_CONSOLE = "%(log_color)s%(asctime)s [%(levelname)s] %(message)s"
logging.root.setLevel(LOG_LEVEL)

# 自定义log level
SUCCESS = 24
FAIL = 25
logging.addLevelName(SUCCESS, 'SUCCESS')
logging.addLevelName(FAIL, 'FAIL')

formatter_console = colorlog.ColoredFormatter(
    LOG_FORMAT_CONSOLE,
    datefmt="%H:%M:%S",
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'SUCCESS': 'bold_green',
        'FAIL': 'bold_red',
        'WARNING': 'bold_yellow',
        'ERROR': 'red'
    },
    secondary_log_colors={},
    style='%'
)

handler_stream = logging.StreamHandler()
handler_stream.setLevel(LOG_LEVEL)
handler_stream.setFormatter(formatter_console)

log = logging.getLogger("Setu")
log.setLevel(LOG_LEVEL)
log.addHandler(handler_stream)


def debug(msg):
    log.debug(msg)


def info(msg):
    log.info(msg)


def warn(msg):
    log.warning(msg)


def error(msg):
    log.error(msg)


def fail(msg):
    log.log(FAIL, msg=msg)


def success(msg):
    log.log(SUCCESS, msg=msg)
