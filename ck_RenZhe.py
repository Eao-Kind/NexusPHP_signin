"""
cron: 5 6 * * *
new Env('忍者');
"""

from notify import *
from util import *

import requests


class RenZhe:
    def __init__(self, check_items):
        self.check_items = check_items
        self.my_init()

    def my_init(self):
        self.url = self.check_items.get("url")
        self.username = self.check_items.get('username')
        self.password = self.check_items.get('password')
        self.signInUrl = self.check_items.get("signInUrl")
        self.cookie = get_cookie_by_json("RenZheCookie")
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
            "cookie": self.cookie,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }

    def get_cookie_by_requests(self):
        """
        使用requests登录拿cookie
        :return:
        """
        sess = requests.Session()
        html = sess.get(self.url, headers=self.headers).text
        form_data = {
            'email': self.username,
            'passwd': self.password,
            'code': '',
            'remember_me': 'on'
        }
        html = sess.post(self.check_items["signUrl"], data=form_data)
        print(html.text)
        cookie = sess.cookies
        cookie_list = cookie.get_dict()
        cookie = [item + '=' + cookie_list[item] for item in cookie_list]
        new_cookie = '; '.join(item for item in cookie)
        print(new_cookie)
        msg = modify_cookie(self.__class__.__name__ + "Cookie", new_cookie)
        return msg

    def check(self):
        # 测试cookie是否有效
        r = requests.get(self.url, headers=self.headers, verify=False)
        r.encoding = "utf-8"
        # print(r.text)
        html = re.match('.*会员时(.*?)', r.text, re.S)
        if html:
            return True
        return False

    def sign(self):
        r = requests.post(self.signInUrl, headers=self.headers, data=data, verify=False)
        if r.status_code == 200:
            print(r.text)
            # 签到成功 、已经签到过了  unicode编码 "msg": "\u4f60\u83b7\u5f97\u4e86 195 MB\u6d41\u91cf",
            msg = r.json()["msg"]
            return msg
        else:
            msg = "状态码" + str(r.status_code)
            print(msg)

    def main(self):
        msg_all = ""
        global j
        j += 1
        if j > 4:  # 防止由于识别出错而导致一直递归
            return "连续失败多次，cookie可能更新不成功！"
        if not self.check():
            msg = "cookie失效或网站暂时无法访问,开始使用登录更新cookie....."
            print(msg)
            msg_all += msg
            msg = self.get_cookie_by_requests()
            print(msg)
            print("正在重新初始化请求头")
            self.my_init()
            msg_all += msg
            self.main()
        else:
            msg = self.sign()
            print(msg)
            msg_all += msg
            return msg_all


if __name__ == '__main__':
    j = 3
    data = get_data()
    _check_items = data.get("RenZhe", [])
    meg = RenZhe(check_items=_check_items).main()
    send("忍者", meg)