import requests
from predict import *
import http.cookiejar as cookielib
import re
import json


def sign_in(web_name):
    bt_Session = requests.session()  
    os.chdir('../cookies')           # 切换到cookie目录
    try:
        bt_Session.cookies = cookielib.LWPCookieJar(filename=web_name + '.txt')
        bt_Session.cookies.load()  # 加载cookie
        #s = bt_Session.get(url[web_name], headers=headers)
        #print(s.text)
        return bt_Session
    except:
        print("{}的cookies加载失败".format(web_name))
        return None


def submitdata(web_name, imagehash, predictlabel):
    if web_name == 'HDSky':
        date = {
            'action': 'showup',
            'imagehash': imagehash,
            'imagestring': predictlabel,
        }
    elif web_name == 'OpenCD':
        date = {
            'imagehash': imagehash,
            'imagestring': predictlabel,
        }
    elif web_name == 'btschool':
        date = {
            'action': 'addbonus',
        }

    elif web_name == 'HDChina':
        date = {
            'csrf': '812f2ecf1a6db185468944c748ed9b412d551143',
        }
    elif web_name == 'TTG':
        date = {
            'signed_timestamp': '1581092163',
            'signed_token': '844ffc6e53e89f4d70e65f6161e74600',
        }
    else:
        return None
    return date


# 判断是否签到成功  不同站点有差别，暂时未适配
def decide_if_signin_ok(web_name, s):
    print("判断是否成功还未写好")



def get_imgurl(web_name, session):
    if web_name == 'OpenCD':  
        req = session.post(checkin_php[web_name], headers=headers)  
    else:
        data = json.loads(date[web_name])  # 获取需要发送的data
        # print(data, type(data))
        req = session.post(checkin_php[web_name], headers=headers, data=data)  
    #print(req.text)
    if web_name == 'HDSky':
        listimageHash = re.findall('.*?code":"(.*?)"', req.text)  # 提取Hash列表
    elif web_name == 'OpenCD':
        listimageHash = re.findall('.*?imagehash=(.*?)" border="0"/>', req.text)  # 提取Hash列表
    imageHash = "".join(listimageHash)  # 列表转换为字符串
    imgurl = url_img[web_name] + '/image.php?action=regimage&imagehash=' + imageHash  
    return imgurl, imageHash


def main(web_name):
    #print('正在登陆！')
    try:
        session = sign_in(web_name)  # 登录
        if web_name in ['HDSky', 'OpenCD', 'HDChina']:  # 如果需要验证码
            #print('正在获取图片链接！')
            imgurl, imageHash = get_imgurl(web_name, session)  # 获取图片url
            #print(imgurl, imageHash)
            with open('temp.png', 'wb') as f:
                f.write(session.post(imgurl).content)  # 写入图片
            print('正在使用神经网络！')
            predictlabel = predict(Image.open('temp.png'))  # 使用神经网络预测验证码
            print(predictlabel)
            print('正在构建验证码data！')
            data = submitdata(web_name, imageHash, predictlabel)  # 构建提交验证码的数据
            print(data)
            s = session.post(post_submit[web_name], headers=headers, data=data)    # 提交验证码
        else:
            print('正在构建data！')
            data = submitdata(web_name, None, None)
            s = session.get(signin_ok[web_name], data=data)  # 提交签到
        decide_if_signin_ok(web_name, s)  # 判断是否签到成功
    except:
        print("{}签到出错".format(web_name))


if __name__ == '__main__':
    for web_name in neednamelist:
        session = sign_in(web_name)  
