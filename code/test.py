# -*- coding: utf-8 -*-
import requests
from predict import *
import http.cookiejar as cookielib
import re
from PIL import Image
import json

# 加载cookies到会话
def sign_in(web_name):
    bt_Session = requests.session()  # 创建一个会话
    os.chdir('../cookies')
    # 切换到cookie目录
    bt_Session.cookies = cookielib.LWPCookieJar(filename=web_name + '.txt')
    bt_Session.cookies.load()  # 加载cookie
    # s = bt_Session.post('https://www.open.cd/index.php', headers=headers)
    # print("0")
    # print(s.text)
    return bt_Session


#判断是否签到成功
def submitdata(web_name, imagehash, predictlabel):
    if web_name == 'OpenCD':
        date = {
            'imagehash': imagehash,
            'imagestring': predictlabel,
        }
    return date

#获取图片hash值
web_name = 'OpenCD'
session = sign_in(web_name)
req = session.get(checkin_php[web_name], headers=headers)  # 模拟请求获取Hash值
listimageHash = re.findall('.*?imagehash=(.*?)" border="0"/>', req.text)
imageHash = "".join(listimageHash)
imgurl = url_img[web_name] + '/image.php?action=regimage&imagehash=' + imageHash  # 组合url链接
print(imgurl)

#使用神经网络预测
with open('temp.png', 'wb') as f:
    f.write(session.get(imgurl).content)  # 写入图片
    f.close()
print('正在使用验证码识别：', end='')
predictlabel = predict(Image.open('temp.png'))+'1'  # 使用神经网络预测验证码
print(predictlabel)
print('正在构建验证码data！')
data = submitdata(web_name, imageHash, predictlabel)  # 构建提交验证码的数据
s = session.get(signin_ok[web_name], data=data)
print(s.text, type(s.text))
if '错' in s.text:
    print("签到失败")
else:
    print("签到成功")

