from aip import AipOcr
from PIL import Image
import re
import os
import json
from utils import vgg_predict
import toml
import requests
from utils import yolov3_predict


def baidu_api(img):
    '''
    使用百度api识别图片，返回识别的结果
    :param img: byte
    :return: srt
    '''
    check_items = toml.load("./config/pt_check.toml")
    # 百度ocr
    BaiDuAPI = check_items.get("BaiDuAPI")
    APP_ID = BaiDuAPI.get("APP_ID")
    API_KEY = BaiDuAPI.get("API_KEY")
    SECRET_KEY = BaiDuAPI.get("SECRET_KEY")
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    print("百度APP_ID:" + APP_ID)
    try:
        res = client.basicGeneral(img)  # 使用百度ocr预测
        return res
    except Exception as e:
        print(e)
    return '0'


def verification_code(srt):
    # 去除验证码里面的无用信息
    # 使用正则去除部分错误并决定是否保留图片
    # print(str)
    try:
        srt = srt['words_result'][0]['words']  # 提取出所需要的字符串
        srt = re.sub(r'[^A-Za-z0-9]', '', srt)  # 去除空格，.号 获取到正确的验证码
        # srt = re.sub("[a-z]", "", srt)  # 去除小写字母，因为验证码不区分大小写
        if len(srt) == 6 and 'Z' not in srt:  # 如果是6个字符则保存，否则为识别错误,改为调用本地模型
            return srt
        elif (str["error_code"] == 216201):  # 图片错误
            return "-1"
        else:
            return '0'
    except Exception as e:
        print(e)
    return None


def identify(img):
    res = baidu_api(img)
    print("百度ocr识别结果：")
    print(res)
    res = verification_code(res)
    if res == '0':  # 百度api识别出错，调用本地
        print("百度ocr失败出错，调用本地模型中....")
        with open('temp.png', 'wb') as f:
            f.write(img)  # 保存一下图片，以便百度识别识别
        img = Image.open('temp.png')
        print("本地模型暂时仅有GPU版本，无法调用，请训练cpu")
        res = vgg_predict.predict(img)
    elif res == "-1":  # 图片错误，可能是请求有问题
        pass
    return res


def yolov3_identify(img):
    try:
        offest = yolov3_predict.predict(image=img)
        return offest
    except:
        print("yolov3识别出错，请查看图片")
        exit()


def get_json_data():  # 获取json里面数据
    with open('./config/cookie.json', 'r', encoding='utf8') as f:
        json_data = json.load(f)
        # json_data["HDSkyCookie"] = cookie_str
        dicts = json_data  # 将修改后的内容保存在dict中
    return dicts


def write_json_data(dict):  # 写入json文件
    with open('./config/cookie.json', 'w') as r:
        json.dump(dict, r)


def modify_cookie(pt_name, new_cookie):
    """
    根据站点名称和新cookie修改保存cookie的json文件
    :param pt_name: 如HDSkyCookie
    :param new_cookie: xxxxx
    :return:
    """
    try:
        dicts = get_json_data()
        dicts[pt_name] = new_cookie
        write_json_data(dicts)
        return "更新cookie成功," + new_cookie
    except Exception as e:
        print(e)
        return "更新cookie失败"


def get_data() -> dict:
    """
    获取签到的配置文件。
    :return: 签到配置文件对象
    """
    check_config = "./config/pt_check.toml"
    if not os.path.exists(check_config):
        print("错误：未检查到签到配置文件，请在指定位置创建文件或设置 CHECK_CONFIG 指定你的文件。")
        exit(1)

    DATA = toml.load(check_config)
    return DATA


def get_cookie_by_json(web_name):
    # 从环境变量获取 或者 从配置文件获取 或者调用模拟登录获取
    if web_name in os.environ:
        cookie = os.environ[web_name]
        print("已获取并使用Env环境" + web_name + cookie)
        return cookie
    with open('./config/cookie.json', 'r', encoding='utf8') as f:
        json_data = json.load(f)
        try:
            cookie = json_data[web_name]
            print("cookie获取成功")
            return cookie
        except Exception as e:
            print(e)
            print(web_name + "获取cookie失败")
            exit(1)


def createFs(uid, proxyurl):
    """
    创建一个uid实例
    :param uid: sessionsUid
    :param url: proxyIP
    :return: 成功 <Response [200]> 失败 <Response [502]>
    """
    # print(uid, url)
    payload = json.dumps({
        "cmd": "sessions.create",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "session": uid  # 创建个实例
    })
    headers = {'Content-Type': 'application/json'}
    res = requests.request("POST", url=proxyurl, headers=headers, data=payload)
    print(res)
    if str(res) == "<Response [200]>":
        return 1
    elif str(res) == "<Response [502]>":
        print("502错误")
        return 0
    else:
        print("创建代理实例出现未知错误")
        return -1


def destroyFs(uid, proxyurl):
    """
    创建一个uid实例
    :param uid: sessionsUid
    :param url: proxyIP
    :return: 成功 <Response [200]> 失败 <Response [502]>
    """
    payload = json.dumps({
        "cmd": "sessions.destroy",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "session": uid  # 销毁实例
    })
    headers = {'Content-Type': 'application/json'}
    res = requests.request("POST", url=proxyurl, headers=headers, data=payload, allow_redirects=True)
    print(res)
    if str(res) == "<Response [200]>":
        return 1
    elif str(res) == "<Response [502]>":
        print("502错误")
        return 0
    else:
        print("销毁代理实例出现未知错误")
        return -1


def fs(url, method, session, proxyurl):
    print(url, method, session)
    if session:
        payload = json.dumps({
            "cmd": method,
            "url": url,
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "session": session,
        })
    else:
        payload = json.dumps({
            "cmd": method,
            "url": url,
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        })
    headers = {'Content-Type': 'application/json'}
    res = requests.request("POST", url=proxyurl, headers=headers, data=payload)
    if str(res) == "<Response [200]>":
        return res
    elif str(res) == "<Response [502]>":
        print("502错误")
        return 0
    else:
        print("代理未知错误")
        return -1
