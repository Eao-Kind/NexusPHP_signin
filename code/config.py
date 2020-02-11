import os
import re


neednamelist = ['btschool']


headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gec、'
                      'ko) Chrome/79.0.3945.130 Safari/537.36', }


# 请求验证码的url，只有需要url_img的网址才会用到这个
checkin_php = {
    'HDSky': '？？',
    'OpenCD': '？？？plugin_sign-in.php', }


# 获取验证码hash的表单数据，只有需要url_img的网址才会用到这个
date = {
    'HDSky': '{"action": "new"}',
    'OpenCD': '1', }


# 提交验证码url，只有需要url_img的网址才会用到这个
post_submit = {
    'HDSky': '？？？showup.php',
    'OpenCD':'？？？plugin_sign-in.php?cmd=signin', }


# 用于组合图片地址
url_img = {
    'HDSky': '',
}


# 用于签到
signin_ok = {
    'btschool': '？？？index.php?action=addbonus',
}


# 验证码识别所需配置
NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
ALL_CHAR_SET = NUMBER + ALPHABET
ALL_CHAR_SET_LEN = len(ALL_CHAR_SET)
MAX_CAPTCHA = 6


#处理cookies
def cookies(web_name):
    with open(web_name, 'r') as f:
        lnum, data = 0, '#LWP-Cookies-2.0\n'   # 从饼干获取到的格式头不对，此处进行替换
        temp = f.readlines()  
        if temp[0] == "// Semicolon separated Cookie File\n":  # 判断是否未处理的文本:
            for line in temp[4:]:
                #print(line)
                data += line
            temp = re.sub('expires="(.*?)"', 'expires="2038-01-19 03:14:07Z"', data)  
            f.close()
            with open(web_name, 'w') as f:
                f.write(temp)
                f.close()
                print("{}cookie已处理".format(web_name))


if __name__ == '__main__':
    os.chdir('../cookies')
    file = os.listdir()
    print(file)
    for text in file:
        if text[-3:] == 'txt':
            cookies(text)
