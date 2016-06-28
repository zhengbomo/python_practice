#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, render_template
from Analyzer import Analyzer
import json
import collections


app = Flask(__name__)
app.jinja_env.add_extension("chartkick.ext.charts")


@app.route('/')
def index():
    urls = ['/percent/10',
            '/percent/北京/10',
            '/percent/广州/10',

            '/salary/10',
            '/salary/北京/10',
            '/salary/广州/10',

            '/key/iOS/10',
            '/key/Python/10',
            ]
    atags = ''
    for url in urls:
        atags += '<a href="{0}" target="_blank">{0}</a><br/><br/>'.format(url)
    return atags


@app.route('/percent/<count>')
@app.route('/percent/<city>/<count>')
def job_percent_for_city(city=None, count=0):
    """ 职位的数量排行
    :param count: 结果数
    :param city: 关键字
    """
    analyzer = Analyzer()
    data = analyzer.key_persent(count=count, city=city)
    data = collections.OrderedDict(sorted(data.items(),key = lambda t:t[1], reverse=True))
    data = json.dumps(data, encoding='utf-8',indent=4)

    subtitle = u'全国' if city is None else city
    return render_template('index.html', data=data, title=u'职位的数量排行',
                           subtitle=subtitle)


@app.route('/salary/<count>')
@app.route('/salary/<city>/<count>')
def high_salary_for_city(city=None, count=0):
    """ 职位薪资排行
    :param count: 结果数
    :param city: 城市
    """
    analyzer = Analyzer()
    data = analyzer.get_high_salary_jobs(city, count)
    data = collections.OrderedDict(sorted(data.items(),key = lambda t:t[1], reverse=True))
    data = json.dumps(data, encoding='utf-8',indent=4)

    subtitle = u'全国' if city is None else city
    return render_template('index.html', data=data, title=u'城市的薪资排行',
                           subtitle=subtitle)


@app.route('/key/<count>')
@app.route('/key/<key>/<count>')
def salary_for_city(key=None, count=0):
    """ 不同城市iOS的分布
    :param count: 结果数
    :param key: 关键字
    """
    analyzer = Analyzer()
    data = analyzer.get_salary_in_city(key, count)
    data = collections.OrderedDict(sorted(data.items(),key = lambda t:t[1], reverse=True))

    return render_template('index.html', data=json.dumps(data, encoding='utf-8',indent=4), title=u'职位在不同城市的薪资排行',
                           subtitle=key)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
