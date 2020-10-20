import json
import os
import requests
import time


URL_VALIDATE = 'https://www.futbin.com/21/'


class ProxyController:
    def __init__(self, proxy_path):
        self.proxy_path = proxy_path
        
        self.proxy_pool = []
        self.index = 0
        self._reset_proxy()
        

    def _load_proxy_pool(self):
        print("Loading pools")
        while True:
            proxy_pool_legacy = self.proxy_pool
            self.index = 0
            with open(self.proxy_path, "r") as f:
                self.proxy_pool = json.load(f)
            if self.proxy_pool == proxy_pool_legacy or len(self.proxy_pool) == 0:
                print("sleep")
                time.sleep(120)
            else:
                break

    def _remove_proxy(self):
        os.environ.pop('http_proxy', None)
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('https_proxy', None)
        os.environ.pop('HTTPS_PROXY', None)

    def _reset_proxy(self):
        self._remove_proxy()
        while True:
            if self.index == len(self.proxy_pool):
                self._load_proxy_pool()
            proxy = self.proxy_pool[self.index]
            self.index += 1
            print("test on {}".format(proxy))
            if self._validate(proxy):
                break
        proxy_str = "http://" + proxy["https"]
        self.proxy_str = proxy_str
        print("----------------------")
        print("Set for proxy: {}".format(proxy_str))
        print("----------------------")
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
        while True:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code== 200:
                    return response
                else:
                    print("403 for {}".format(self.proxy_str))
                    self._reset_proxy()
            except Exception as e:
                print(e)
                self._reset_proxy()
