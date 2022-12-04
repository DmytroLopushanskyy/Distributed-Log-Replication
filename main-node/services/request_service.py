from requests import put
from threading import Thread

from application.custom_logger import logger
from application.count_down_latch import CountDownLatch


class RequestService:
    def __init__(self, write_concern, timeout=20):
        self.timeout = timeout
        self.latch = CountDownLatch(write_concern)

    def send_payload(self, urls, payload):
        for url in urls:
            self.async_request(self.guarded_put, url, json=payload)

        self.latch.wait()

    def async_request(self, method, *args, **kwargs):
        """
        Makes request on a different thread
        """
        kwargs['hooks'] = {'response': self.request_callback}
        kwargs['timeout'] = self.timeout
        thread = Thread(target=method, args=args, kwargs=kwargs)
        thread.start()
        return thread

    def request_callback(self, response, *_, **__):
        logger.info(f"Response code received: {response.status_code}")
        if response.status_code == 200:
            self.latch.count_down()

    @staticmethod
    def guarded_put(*args, **kwargs):
        try:
            put(*args, **kwargs)
        except Exception as err:
            logger.error(f"Request error: {err}")
