"""
数据可视化
"""
import jieba  # 分词，将一个中文句子分为词语
from matplotlib import pyplot as plt  # 数据可视化
import matplotlib.ticker as ticker
from wordcloud import WordCloud  # 词云
from PIL import Image  # 图片处理
import numpy as np  # 矩阵运算
import numpy as np
import xlrd
import pymysql


def read_xls():
    """
    读取数据库
    return: 数据
    """
    data = []
    db = pymysql.connect(host='127.0.0.1', user='root', password='1234', database='bigdata')
    cursor = db.cursor()
    sql = 'select * from test;'
    cursor.execute(sql)
    while True:
        row = cursor.fetchone()
        if not row:
            break
        # print(data)
        data.append(row)
    # print(data)
    return data

def get_wordcloud(data, col):
    """
    data: xls数据
    col: data数据中对应项的列数
    """
    text = ''
    for i in range(len(data)):
        text += data[i][col]

    # 分词
    cut = jieba.cut(text)
    string = ' '.join(cut)

    stopwords = set()
    content = [line.strip() for line in open(r'data/stopwords.txt', 'r', encoding='UTF-8').readlines()]
    stopwords.update(content)

    # 词云制作
    wc = WordCloud(
        background_color='white',
        font_path='simkai.ttf',
        stopwords=stopwords
    )
    wc.generate_from_text(string)

    # 绘制图片
    plt.figure('词云')
    plt.plot()
    plt.imshow(wc)
    plt.axis('off')
    plt.savefig(r'data/wordcloud.jpg')


def get_time(data, col, ax):
    """
    获得对应电影的的值作时间
    data: xls数据
    col: data数据中对应项的列数
    """
    time = []
    for i in range(len(data)):
        time.append(data[i][col])
    time_count = {}
    for i in time:
        if i in time_count:
            time_count[i] = time_count[i] + 1
        else:
            time_count[i] = 1

    x = [int(i) for i in time_count.keys()]
    x.sort()
    y = [time_count[str(i)] for i in x]

    #  第一子图绘制柱状图
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # fig, ax = plt.subplots()
    plt.axis('on')
    mean = np.mean(y)
    ax.axhline(y=mean, color='r')
    # 绘制柱状图
    ax.bar(x, y, align='center')
    ax.set_xlabel('时间/年')
    ax.set_ylabel('数量/部')
    ax.set_title('每一年进top250电影的数量')


def get_score_and_people(data, col_score, col_peo, ax):
    """
    data: xls数据
    col_score: score对应的列
    col_peo: people对应的列
    """
    scores = []
    people = []
    for i in range(len(data)):
        scores.append(data[i][col_score])
        people.append(int(data[i][col_peo]))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # fig, ax = plt.subplots()
    ##################################
    scores = [float(i) for i in scores]
    print('方差:', np.var(scores))
    result = np.corrcoef(scores, people)
    print('评分与人数相关性', result)
    ax.scatter(scores, people)
    ax.set_title('评分与评分人数的相关性')
    ax.set_xlabel('评分')
    ax.set_ylabel('评分人数')


def get_country(data, col, ax):
    """
    对电影国家进行排序，得到饼图
    data: xls数据
    col: 对应国家数据
    """
    countries = []
    for i in range(len(data)):
        country = data[i][col]
        country = country.split(' ')
        for i in country:
            countries.append(i)
    countries_count = {}
    for key in countries:
        if key in countries_count:
            countries_count[key] = countries_count[key] + 1
        else:
            countries_count[key] = 1
    sorted_item = sorted(countries_count.items(), key=lambda x: x[1], reverse=True)
    labels = []
    sizes = []
    for i in sorted_item:
        labels.append(i[0])
        sizes.append(i[1])
    explode_list = [0 for i in range(10)]
    explode_list[0] = 0.1
    explode = tuple(explode_list)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    ax.pie(sizes[:10], labels=labels[:10], autopct='%1.1f%%',
           shadow=True, startangle=90, textprops=dict(color="w"))
    ax.legend(title="国家", loc=2, bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title('电影制作国（前十）')


def get_type(data, col, ax):
    """
    得到电影的类型
    data: xls数据
    col: 对应国家数据
    """
    types = []
    for i in range(len(data)):
        type = data[i][col]
        type = type.strip()
        type = type.split(' ')
        for i in type:
            types.append(i)
    type_count = {}
    for key in types:
        if key in type_count:
            type_count[key] = type_count[key] + 1
        else:
            type_count[key] = 1
    sorted_item = sorted(type_count.items(), key=lambda x: x[1], reverse=False)

    # 绘制横向条形图
    plt.rcdefaults()
    plt.rcParams['font.sans-serif'] = ['SimHei']
    x = [i[0] for i in sorted_item]
    y = [i[1] for i in sorted_item]
    hbars = ax.barh(x, y, align='center')
    ax.bar_label(hbars, padding=8, color='black', fontsize=12)
    ax.set_xlabel('数量')
    ax.set_title('电影题材')


if __name__ == '__main__':
    xls_data = read_xls()
    # 电影详情链接	图片链接	影片中文名	影片外国名	评分	评价数	概况	相关信息	时间	国家	类型
    # 0            1          2          3           4      5       6       7          8      9       10
    get_wordcloud(xls_data, 6)
    fig, axes = plt.subplots(2, 2)
    fig.canvas.set_window_title('统计数据')
    fig.suptitle('统计数据', fontsize=18)
    plt.plot()
    get_time(xls_data, 8, axes[0, 0])
    get_score_and_people(xls_data, 4, 5, axes[0, 1])
    get_country(xls_data, 9, axes[1, 0])
    get_type(xls_data, 10, axes[1, 1])
    plt.savefig(r'data/statistic.png', dpi=1000)
    plt.show()


