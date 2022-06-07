"""
cron: 5 6 * * *
new Env('PTHDHome');
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from notify import *
from util import *

import requests


class HDHome:
    def __init__(self, check_items):
        self.check_items = check_items
        self.my_init()

    def my_init(self):
        self.url = self.check_items.get("url")
        self.username = self.check_items.get('username')
        self.password = self.check_items.get('password')
        self.imgUrl = self.check_items.get('imgUrl')
        self.signInUrl = self.check_items.get("signInUrl")
        self.cookie = get_cookie_by_json("HDHomeCookie")
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
            "cookie": self.cookie,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }

    def driver_init(self, check_items):
        """
        只有需要使用driver获取cookie时才初始化
        :param check_items:
        :return:
        """
        self.imgUrl = self.check_items.get("imgUrl")
        self.username = self.check_items.get("username")
        self.password = self.check_items.get("password")
        # driver选择器
        self.nameSelect = self.check_items.get("nameSelect")
        self.passwordSelect = self.check_items.get("passwordSelect")
        self.verificationSelect = self.check_items.get("verificationSelect")
        self.submitSelect = self.check_items.get("submitSelect")

    def sign_in_by_driver(self):
        """
        启动浏览器——打开登录界面——获取图片——使用识别——登录
        :return:
        """
        browser = webdriver.Chrome()
        browser.get(self.url)
        html = browser.execute_script("return document.documentElement.outerHTML")  # 执行js代码返回html页面内容
        imgHash = re.match('.*?imagehash=(.*?)\" border', html, re.S).group(1)
        self.imgUrl += imgHash  # 组合获取图片的地址
        print("Hash = {},图片url={}".format(imgHash, self.imgUrl))
        img = requests.get(self.imgUrl).content  # 获取图片的二进制文本， 发现和使用百度ocr所使用的图片样式一样
        # with open('temp.png', 'wb') as f:
        #     f.write(img)
        res = identify(img)
        # 输入账户密码，验证码 登录 暂不支持有二级验证
        browser.find_elements(by=By.CSS_SELECTOR, value=self.nameSelect)[0].send_keys(self.username)
        browser.find_elements(by=By.CSS_SELECTOR, value=self.passwordSelect)[0].send_keys(self.password)
        browser.find_elements(by=By.CSS_SELECTOR, value=self.verificationSelect)[0].send_keys(res)
        browser.find_elements(by=By.CSS_SELECTOR, value=self.submitSelect)[0].click()
        return browser

    def get_cookie_by_driver(self):
        """
        获取cookie并写入json
        :return:
        """
        # 处理cookie
        browser = self.sign_in_by_driver()
        # 获取cookie
        cookie_list = browser.get_cookies()
        cookie = [item['name'] + '=' + item['value'] for item in cookie_list]
        cookie_str = '; '.join(item for item in cookie)
        print(cookie_str)
        msg = modify_cookie("HDSkyCookie", cookie_str)
        return msg

    def get_cookie_by_requests(self):
        """
        使用requests登录拿cookie
        :return:
        """
        sess = requests.Session()
        # sess.headers = self.headers
        # del sess.headers['cookie']
        html = sess.get(self.url, headers=self.headers).text
        imghash = re.match('.*?imagehash=(.*?)\" border', html, re.S).group(1)
        imgUrl = self.imgUrl + imghash
        img = sess.get(imgUrl).content
        res = identify(img)
        print("图片识别结果：" + res + ",图片地址：" + imgUrl)
        form_data = {
            'username': self.username,
            'password': self.password,
            'oneCode': '',
            'imagestring': res,
            'imagehash': imghash
        }
        sess.post(self.check_items["signUrl"], data=form_data)
        sess.get("https://hdhome.org/userdetails.php?id=9")
        cookie = sess.cookies
        cookie_list = cookie.get_dict()
        cookie = [item + '=' + cookie_list[item] for item in cookie_list]
        new_cookie = '; '.join(item for item in cookie)
        msg = modify_cookie(self.__class__.__name__+"Cookie", new_cookie)
        return msg

    def check(self):
        # 测试cookie是否有效
        r = requests.get(self.url, headers=self.headers)
        r.encoding = "utf-8"
        # print(r.text)
        html = re.match('.*欢迎(.*?)', r.text, re.S)
        if html:
            return True
        return False

    def get_info(self, url):
        # 请求页面拿到html文件——提取信息——放入info对象的属性里
        r = requests.get(url, headers=self.headers)
        r.encoding = 'utf-8'
        html = r.text
        # 提取信息的正则表达式规则，后期可提取
        try:
            name = re.match('.*class=\'EliteUser_Name\'><b>(.*?)</b>', html, re.S).group(1)
            print(name)
            moli = re.match('.*魔力值 </font>\[<a href="mybonus.php">使用</a>]: (.*?) <font', html, re.S).group(1)
            print(moli)
            share = re.match('.*分享率：</font> (.*?) <a', html, re.S).group(1)
            print(share)
            msg = "用户名：" + name + "\n魔力值：" + moli + "\n分享率:" + share
            return msg
        except Exception as e:
            print(e)

    def sign(self):
        r = requests.post(self.signInUrl, headers=self.headers, data=data)
        if r.status_code == 200:
            print(r.text)
            # 签到成功 、已经签到过了
            msg = re.match(".*本次签到获得 <b>(.*?)</b> 个魔力值", r.text, re.S)
            if msg:  # 成功
                msg = msg.group(1)
            else:
                msg = "\n今天已经签到过了"
            return msg
        else:
            msg = "状态码" + str(r.status_code)
            print(msg)

    def main(self):
        global j
        msg_all = ""
        msg = "正在进行第" + str(j) + "次尝试\n"
        print(msg)
        msg_all += msg
        j += 1
        if j > 4:  # 防止由于识别出错而导致一直递归
            print("连续失败多次，cookie可能更新不成功！")
            exit(1)
        if not self.check():
            msg = "cookie失效或网站暂时无法访问,开始使用登录更新cookie....."
            print(msg)
            msg_all += msg
            # msg = self.get_cookie_by_driver()
            msg = self.get_cookie_by_requests()
            print(msg)
            print("正在重新初始化请求头")
            self.my_init()
            msg_all += msg
            self.main()
        else:
            msg = self.sign()
            msg = "今天签到获得魔力值" + str(msg)
            print(msg)
            msg_all += msg
            return msg_all


if __name__ == '__main__':
    j = 1
    data = get_data()
    _check_items = data.get("HDHome", [])
    meg = HDHome(check_items=_check_items).main()
    # send("HDSky", meg)
