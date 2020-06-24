# lofterSpider
### 功能介绍
抓取lofter tag归档，备份到本地数据库，导出图片和文章
1. 备份lofter指定tag下全部档案到本地数据库。
2. 将数据库中的内容导出成txt并下载相关图。

### 使用方法
#### 版本要求
python3.7
java >8
#### 依赖解决：方法一
##### 设置虚拟环境
```shell
>> pip3 install virtualenv
>> virtualenv -p python3 .env
>> source .env/bin/active
# 成功后，应该出现这样的结果
>> which python
...lofterSpider/.env/bin/python3
```
##### 安装`pipenv`，解决依赖关系
```shell
>> pip3 install pipenv
>> pipenv install
# 成功后，应该出现如下结果
>> pip3 freeze
...
beautifulsoup4==4.9.1
html5lib==1.0.1
...
mysqlclient==1.4.6
pipenv==2020.6.2
requests==2.24.0
...
SQLAlchemy==1.3.17
urllib3==1.25.9
...
```
#### 依赖解决：方法二
##### 手动安装
```
>> pip3 install sqlalchemy, html5lib, bs4, requests
```
##### 修改配置文件
在`config.py`中设置数据库名称，前缀，导出黑名单和热度限制等。
##### 运行
```shell
>> python3 run.py
```
