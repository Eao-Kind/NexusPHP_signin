# Signin

自用、自动签到

默认环境变量中存在通知信息等环境变量

# 拉库

>  https://github.com/Eao-Kind/NexusPHP_signin.git 

白名单：ck_|ins_

执行后

> cp -r /ql/data/repo/Eao-Kind_NexusPHP_signin_master/utils /ql/scripts/Eao-Kind_NexusPHP_signin_master/



# 降级

pytorch无法运行可能是python版本太高，需要降级python到3.6

查找当前python安装路径

```cmd
find / -name "python3.9*"    
whereis python3.9
rm /usr/bin/python3
rm /usr/bin/pip3
```



安装python3.6版本

```cmd
cd /home
wget https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tgz
tar -zxvf Python-3.6.0tgz
cd Python-3.6.0

./configure --prefix=/usr/local/python3  # 配置安装路径

make && make install
cd /usr/local/python3/bin/

ln -s /usr/local/python3/bin/python3.6 /usr/bin/python3

ln -s /usr/local/python3/bin/pip3.6 /usr/bin/pip3
python3 --version
```



# 依赖

```sh
curl -fsSL https://git.metauniverse-cn.com/https://raw.githubusercontent.com/shufflewzc/QLDependency/main/Shell/QLOneKeyDependency.sh | sh

pip3 install numpy==1.14.0 -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
```



运行 ins_pt_pkg.sh 拉取依赖库

**torch安装**

官网拿命令：https://pytorch.org/get-started/locally/

> ```
> pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
> ```

下载模型文件 yovol3和vgg预测文件16.pth，分别放入/ql/script/utils/yolov3和vgg目录

文件地址



**缺少ld-linux-x86-64.so**



测试

```cmd

```



# 配置

修改config/pt_check_sample.toml文件并修改名称为pt_check.toml，然后把该文件放到 /ql/scripts/Eao-Kind_NexusPHP_signin_master/config 里面



# 其他

网站500错误的异常没有处理
