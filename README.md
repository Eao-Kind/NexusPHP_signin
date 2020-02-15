# NexusPHP_signin
PT站自动签到，使用VGG识别验证码
一.使用方法
  1.获取cookies，以txt格式把cookies按照站点名字放至cookies文件夹内。可以使用小饼干导出，导出格式设置为Perl::LWP，可以在选项里面设置
  2.在config.py文件里，添加需要签到的站点到needwebnamelist=[]，并运行一下config.py 把小饼干导出的格式转换为符合使用的格式
  3.运行signin.py
