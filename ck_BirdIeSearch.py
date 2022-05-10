"""
cron: 5 6 * * *
new Env('小鸟搜索');
"""

import requests
from notify import *
from util import *


class BirdIeSearch:
    def __init__(self, check_items):
        self.check_items = check_items
        self.my_init()

    def my_init(self):
        self.cookie = get_cookie_by_json("BirdIeSearchCookie")
        self.signInUrl = self.check_items.get("signInUrl")
        self.url = self.check_items.get("url")
        self.headers = {
            "Host": "www.birdiesearch.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
            "Referer": "https://www.birdiesearch.com/",
            "Content-Type": "application/json;charset=utf-8",
            "Accept": "application/json, text/plain, */*",
            "cookie": self.cookie,
            "Origin": "https://www.birdiesearch.com"
        }

    def check(self):
        # 测试cookie是否有效
        r = requests.get(self.url, headers=self.headers)
        r.encoding = "utf-8"
        # print(r.text)
        html = re.match('.*登录帐号：(.*?)', r.text, re.S)
        if html:
            return True
        return False

    def sign(self):
        r = requests.post(self.signInUrl, headers=self.headers, verify=False)
        if r.status_code == 200:
            msg = r.json()
            print(msg["msg"])
            return msg["msg"]
        else:
            msg = "状态码" + str(r.status_code)
            print(msg)

    def get_cookie_by_requests(self):
        return "test"

    def main(self):
        msg_all = ""
        if not self.check():
            msg = "cookie失效或网站暂时无法访问,开始使用登录更新cookie....."
            print(msg)
            msg_all += msg
            msg = self.get_cookie_by_requests()
            print(msg)
            self.main()
        else:
            msg = self.sign()
            print(msg)
            msg_all += msg
            return msg_all


if __name__ == '__main__':
    data = get_data()
    _check_items = data.get("BirdIeSearch", [])
    meg = BirdIeSearch(check_items=_check_items).main()
    send("小鸟搜索", meg)
