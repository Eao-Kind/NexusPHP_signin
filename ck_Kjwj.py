"""
cron: 5 6 * * *
new Env('科技玩家');
参考：https://github.com/leafTheFish/DeathNote/blob/main/kjwj.js
在登录完成后拿到全部的cookie请求签到会失败，仅需token，但仅有token的cookie请求首页会无法得到登录信息
"""

from notify import *
from util import *
import requests


class Kjwj:
    def __init__(self, check_items):
        self.check_items = check_items
        self.my_init()

    def my_init(self):
        self.url = self.check_items.get("url")
        self.username = self.check_items.get('username')
        self.password = self.check_items.get('password')
        self.signInUrl = self.check_items.get("signInUrl")
        self.cookie = get_cookie_by_json("KjwjCookie")
        self.authorization = get_cookie_by_json("KjwjAuthorization")
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
            "cookie": self.cookie,
            "origin": "https://www.kejiwanjia.com",
            "referer": "https://www.kejiwanjia.com/mission/today",
            "authorization": self.authorization
        }

    def get_cookie_by_requests(self):
        """
        使用requests登录拿cookie,首先请求 在响应头拿到b2_token作为cookie
        :return:
        """
        form_data = {
            'nickname': '',
            'username': self.username,
            'password': self.password,
            'code': '',
            'img_code': '',
            'invitation_code': '',
            'token': '',
            'smsToken': '',
            'luoToken': '',
            'confirmPassword': '',
            'loginType': ''
        }
        res = requests.post(self.check_items["signUrl"], data=form_data, headers=self.headers)
        print(res.content)
        modify_cookie(self.__class__.__name__ + "Authorization", "Bearer " + res.json()["token"])
        msg = modify_cookie(self.__class__.__name__ + "Cookie", "b2_token=" + res.json()["token"])
        return msg

    def get_user_mission(self):
        url = 'https://www.kejiwanjia.com/wp-json/b2/v1/getUserMission'
        data = {
            'count': '10',
            'paged': '1',
        }
        headers = {
            'Authorization': self.headers["authorization"],
            'Cookie': self.headers["cookie"],
            'Origin': 'https://www.kejiwanjia.com',
            'Referer': 'https://www.kejiwanjia.com/mission/today',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }
        res = requests.post(url=url, headers=headers, data=data)
        # print(res.json())
        return res

    def sign(self):
        r = requests.post(self.signInUrl, headers=self.headers, verify=False)
        if r.status_code == 200:
            msg = r.json()
            credit = msg["credit"]  # 获取积分
            my_credit = msg["mission"]["my_credit"]  # 当前现有积分
            if credit:  # 成功
                msg = "签到成功，获得{}积分，现有积分{}".format(credit, my_credit)
                print(msg)
            else:
                msg = "\n今天已经签到过了"
            return msg
        else:
            msg = "状态码" + str(r.status_code)
            print(msg)

    def main(self):
        msg_all = ""
        self.get_cookie_by_requests()
        self.my_init()
        res = self.get_user_mission()
        print(res.json())
        res = res.json()["mission"]["credit"]
        if res == 0:
            msg = self.sign()
            msg_all += msg
            return msg_all
        else:
            print("今天已签到,获得了" + str(res) + "积分")


if __name__ == '__main__':
    data = get_data()
    _check_items = data.get("Kjwj", [])
    meg = Kjwj(check_items=_check_items).main()
    send("Kjwj", meg)
