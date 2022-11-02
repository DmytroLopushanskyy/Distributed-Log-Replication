import logging
from colorlog import ColoredFormatter


class LoggingHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        # logging attributes: https://docs.python.org/3/library/logging.html#logrecord-attributes
        fmt = "%(log_color)s%(asctime)-25s %(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
        fmt_date = '%Y-%m-%d %H:%M:%S'
        formatter = ColoredFormatter(fmt, fmt_date)
        self.setFormatter(formatter)


logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.addHandler(LoggingHandler())
