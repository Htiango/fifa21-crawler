import json
import os
import requests
import time
import logging
import logging.config


logging.config.fileConfig(fname='logging.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

URL_VALIDATE = 'https://www.futbin.com/21/'
USAGE_THRESHOLD = 360


class ProxyController:
    def __init__(self, proxy_path):
        self.proxy_path = proxy_path
        
        self.proxy_pool = []
        self.index = 0
        self._reset_proxy()
        self.usage = 0
        

    def _load_proxy_pool(self):
        logger.info("Loading pools")
        while True:
            proxy_pool_legacy = self.proxy_pool
            self.index = 0
            with open(self.proxy_path, "r") as f:
                self.proxy_pool = json.load(f)
            if self.proxy_pool == proxy_pool_legacy or len(self.proxy_pool) == 0:
                logger.info("sleep")
                time.sleep(120)
            else:
                break

    def _remove_proxy(self):
        os.environ.pop('http_proxy', None)
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('https_proxy', None)
        os.environ.pop('HTTPS_PROXY', None)

    def _reset_proxy(self):
        logger.info("RESETTING PROXY......")
        self._remove_proxy()
        while True:
            if self.index == len(self.proxy_pool):
                self._load_proxy_pool()
            proxy = self.proxy_pool[self.index]
            self.index += 1
            logger.info("test on {}".format(proxy))
            if self._validate(proxy):
                break
        proxy_str = "http://" + proxy["https"]
        self.proxy_str = proxy_str
        logger.info("----------------------")
        logger.info("Set for proxy: {}".format(proxy_str))
        logger.info("----------------------")
        self.usage = 0
        os.environ['http_proxy'] = proxy_str
        os.environ['HTTP_PROXY'] = proxy_str
        os.environ['https_proxy'] = proxy_str
        os.environ['HTTPS_PROXY'] = proxy_str

    def _validate(self, proxy):
        try:
            response = requests.request("get", URL_VALIDATE, proxies=proxy, timeout=7)
            response_code = response.status_code
            if response_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False

    def get_response(self, url):
        if self.usage > USAGE_THRESHOLD:
            logger.warning("Hitting {} usage threshold".format(USAGE_THRESHOLD))
            self._reset_proxy()
        while True:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code== 200:
                    self.usage += 1
                    return response
                else:
                    logger.info("403 for {}".format(self.proxy_str))
                    self._reset_proxy()
            except Exception as e:
                logger.info("Connection Error for {}".format(self.proxy_str))
                self._reset_proxy()
