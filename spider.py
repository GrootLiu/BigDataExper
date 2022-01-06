"""
爬虫，获取数据
"""
import re  # 正则表达式, 正则表达式，进行文字匹配
import urllib.error  # 指定URL, 获取网页数据
import urllib.request
from bs4 import BeautifulSoup  # 网页解析, 获取数据
import xlwt  # excel操作
import pymysql
import random
import requests
import time


def ask_url(url):
    """
    得到指定URL的网页内容
    :param url: str: 网址
    :return: str: 爬取到的html(str)
    """
    # 模拟浏览器头部信息，向豆瓣服务器发送头部信息
    head = {
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) '
                      'Chrome / 81.0.4044.138 Safari / 537.36'
    }

    # 用户代理：告诉豆瓣服务器，我们是什么类型的机器，浏览器（本质是告诉浏览器，我们可以接受什么水平的文件内容）
    request = urllib.request.Request(url, headers=head)  # request封装
    html = ""
    try:
        response = urllib.request.urlopen(request, timeout=10)
        html = response.read().decode('utf-8')
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
            pass
        if hasattr(e, "reason"):
            print(e.reason)
            pass

    return html


def get_data(base_url):
    """
    爬取网页
    :return: list: 数据列表
    """
    data_list = []  # 新建列表，用于保存数据
    for i in range(10):
        for i in range(0, 10):  # 每页25条信息，一共250条，需要http请求10次
            # 调用获取页面信息的函数，10次
            url = base_url + '?start=' + str(i * 25)
            html = ask_url(url)  # 网页源码(str)
            # 2.逐一解析数据
            # 利用html.parser解析器将html的str解析成树形结构
            soup = BeautifulSoup(html, "html.parser")

            # 影片链接的规则
            find_link = re.compile(r'<a href="(.*?)">')  # 创建正则表达式，表示规则（字符串的模式），提取网页
            # 影片图片的链接规则
            find_img = re.compile(r'<img.*src="(.*?)"', re.S)  # re.S忽略换行符
            # 影片片名
            find_title = re.compile(r'<span class="title">(.*)</span>')
            # 影片评分
            find_rating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
            # 评价人数
            find_judge = re.compile(r'<span>(\d*)人评价</span>')
            # 找到概况
            find_inq = re.compile(r'<span class="inq">(.*)</span>')
            # 找到影片的相关内容
            find_bd = re.compile(r'<p class="">(.*?)</p>', re.S)
            # 从概述中提取相关信息
            bd_find_time = re.compile(r'(\d+)')

            # 从html中查找对应的数据，将其存入list中
            for item in soup.find_all('div', class_="item"):  # 查找符合要求的字符串
                # print(item)  # 查看全部信息
                data = []  # 保存一部电影全部信息
                item = str(item)
                # re库用来通过通过正则表达式查找指定的字符串，防止有重复只提取第一个
                # 影片的具体链接
                link = re.findall(find_link, item)[0]
                data.append(link)  # 添加影片链接
                img_src = re.findall(find_img, item)[0]
                data.append(img_src)  # 添加图片链接
                titles = re.findall(find_title, item)  # 片名可能有多个，不加'[0]'
                if len(titles) == 2:
                    ctitle = titles[0]
                    data.append(ctitle)  # 添加中文名
                    otitle = titles[1].replace("/", "")  # 去掉无关的符号
                    otitle = otitle.replace(" ", "")
                    data.append(otitle)  # 添加非中文电影名
                else:
                    data.append(titles[0])
                    data.append(' ')  # 加入空格占位，防止表格书写错误
                rating = re.findall(find_rating, item)[0]
                data.append(rating)  # 添加评分
                judge_num = re.findall(find_judge, item)[0]
                data.append(judge_num)  # 添加评价人数
                inq = re.findall(find_inq, item)

                if len(inq) != 0:
                    inq = inq[0].replace('。', '，')  # 去掉相应的标点
                    data.append(inq)  # 添加概述
                else:
                    data.append(' ')  # 留空

                bd = re.findall(find_bd, item)[0]
                bd = re.sub(r'<br(\s+)?/>(\s+)?', ' ', bd)  # 去点<\br>
                bd = bd.replace(r' ', '')
                bds = bd.split(r'/')
                country = bds[-2]
                type = bds[-1]
                bd = re.sub('/', ' ', bd)  # 替换'/'
                time = re.findall(bd_find_time, bd)
                data.append(bd.strip())  # 去掉前后的空格
                data.append(time[0])
                data.append(country)
                data.append(type)
                data_list.append(data)  # 将处理好的一部电影信息放入data_list
    print(data_list)
    print(len(data_list))
    return data_list


def save_file(data_list):
    """
    保存数据
    :param data_list: str: 数据内容
    :return: Null
    """
    print('save.....')
    print('共有{}条数据'.format(len(data_list)))

    # 链接数据库
    db = pymysql.connect(host='127.0.0.1', user='root', password='1234', database='bigdata')

    # 游标，对数据库进行操作
    cursor = db.cursor()

    # 创建插入SQL语句
    # sql 语句
    sql = 'insert into test (电影详情链接,图片链接,影片中文名,影片外国名,评分,评分数,概况,相关信息,时间,国家,类型) values (%s, %s, %s, %s, %s, %s, %s, %s, ' \
          '' \
          '%s, %s, %s) '

    for i in range(2500):
        print(i)
        print('第{}条'.format(i))
        data = data_list[i]
        print(data)
        link = data[0]
        imglink = data[1]
        name = data[2]
        engname = data[3]
        grade = data[4]
        gradenum = data[5]
        overview = data[6]
        detail = data[7]
        info = data[8]
        time = data[9]
        typ = data[10]
        values = (link, imglink, name, engname, grade, gradenum, overview, detail, info, time, typ)
        # 执行sql语句
        cursor.execute(sql, values)
        # 在操作完所有操作后，提交修改，推出数据库
    cursor.close()
    db.commit()
    db.close()


if __name__ == "__main__":
    base_url = r"https://movie.douban.com/top250"
    # 1. 爬取网页
    # 2. 解析数据(逐一解析数据)
    data_list = get_data(base_url)
    print(data_list)
    # 3. 保存数据
    save_file(data_list)
    print("爬取完毕")
