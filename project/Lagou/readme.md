学了一段时间的Python，于是抓了一些数据练手，选择了拉勾网上的招聘数据，抓取完成后进行分析，先来看看结果

* 拉勾网只能取到最近一个月的职位，所以以下统计也只有一个月的数据
* 只爬取了技术分类下的数据，如下图
* 总数据有**34122**条，由于拉勾的接口最多只能取到5000条数据，所以其中Android分类和前端开发分类数据可能不全，而其他关键字的结果都不到5000条，数据基本完整

![](http://7xqzvt.com1.z0.glb.clouddn.com/16-6-28/15206332.jpg)

![](http://7xqzvt.com1.z0.glb.clouddn.com/16-6-28/25682703.jpg)

![](http://7xqzvt.com1.z0.glb.clouddn.com/16-6-28/42481592.jpg)

![](http://7xqzvt.com1.z0.glb.clouddn.com/16-6-28/26443417.jpg)

![](http://7xqzvt.com1.z0.glb.clouddn.com/16-6-28/39682738.jpg)

![](http://7xqzvt.com1.z0.glb.clouddn.com/16-6-28/45082468.jpg)

![](http://7xqzvt.com1.z0.glb.clouddn.com/16-6-28/99594263.jpg)

* 可以看到北京薪资最高，
* 安卓需求是iOS的一倍
* 最热门的技术岗位都在前端
* 需求最大的职位是PHP
* CTO，CDN，自然语言处理，GO语言，Hadoop，全栈工程师薪资最高
当然上面只是拉勾网一家最近一个月的数据

## 一、准备
### 1. 要点
* urllib2库的简单使用
* sqlite的使用（入库，统计）
* flask的简单使用
* chartkick的简单使用

分析拉勾网的数据，可以看到，在切换页的时候，数据列表使用ajax异步加载，通过Chrome查看网络数据可以看到数据通过一个Post请求，获取

`http://www.lagou.com/jobs/positionAjax.json?px=default&city=全国&needAddtionalResult=false`
Post数据：`first=false&pn=12&kd=iOS`
pn为页数，kd为搜索关键字

## 二、爬取数据
由于拉勾网的接口没有加密，也没有做限制，爬取的代码很简单，cookie都不用，下面是爬取的代码
```python
@staticmethod
def __download(url, data):
    """下载url内容"""
    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request, data)
        return response.read()
    except Exception, e:
        print str(e)
        return None

if __name__ == '__main__':
    city = u'广州'
    page_num = 10
    keyword = u'iOS'
    url = u'http://www.lagou.com/jobs/positionAjax.json?px=default&city=%s&needAddtionalResult=false' % (city,)
    data = u'first=false&pn=%d&kd=%s' % (page_num, keyword)
    html = __download(url, data)
    if html:
        # 分析入库
        pass
    else:
        logger.error('download fail')
```
爬完之后，我们可以进行分析入库，这里会用到json库

拉勾网的薪资信息使用`**k-**k`, `**k以上`, `**k以下`表示，这里我把他们解析成三个字段：`minsalary`, `midsalary`, `maxsalary`，mid取最大或最小或中间值，`minsalary`和`maxsalary`可空，在统计的时候使用的是`midsalary`作为薪资值

最后我们得到数据库
![](http://7xqzvt.com1.z0.glb.clouddn.com/16-6-28/61622306.jpg)

## 三、分析
接下来是通过浏览器展现图表，这里使用的Flask框架作为Web服务器
### 1. 安装
```bash
$ sudo pip install virtualenv
$ sudo pip install flask

# 图表库
$ sudo pip install chartkick
```

，新建一个模块`ChartServer.py`
```python
#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, render_template

# 下面获取数据或工具类
from Analyzer import Analyzer
import json
import collections

# 构造一个Flask对象，即服务器对象
app = Flask(__name__)
app.jinja_env.add_extension("chartkick.ext.charts")

# 定义路由
@app.route('/percent/<count>')
@app.route('/percent/<city>/<count>')
def job_percent_for_city(city=None, count=0):
    """ 职位的数量排行
    :param count: 结果数
    :param city: 关键字
    """

    # 从数据库中读取数据
    analyzer = Analyzer()
    data = analyzer.key_persent(count=count, city=city)
    # 有序字典
    data = collections.OrderedDict(sorted(data.items(),key = lambda t:t[1], reverse=True))
    data = json.dumps(data, encoding='utf-8',indent=4)

    subtitle = u'全国' if city is None else city

    # 传递参数给模板，并渲染
    return render_template('index.html', data=data, title=u'职位的数量排行', subtitle=subtitle)


if __name__ == "__main__":
    # 运行服务器
    app.run(host="0.0.0.0")
```

模板定义，模板的路径为`/templates/index.html`
```html
<script src="{{ url_for('static', filename='jquery.min.js') }}"></script>
<script src="{{ url_for('static', filename='chartkick.js') }}"></script>
<script src="{{ url_for('static', filename='highcharts.js') }}"></script>

{% line_chart data with library={"title":{"text": title}, "subtitle": {"text": subtitle}} %}
{% pie_chart data with library={"title":{"text": title}, "subtitle": {"text": subtitle}} %}
{% column_chart data with library={"title":{"text": title}, "subtitle": {"text": subtitle}} %}
{% area_chart data with library={"title":{"text": title}, "subtitle": {"text": subtitle}} %}
```
这里使用的几个js文件引用的是本地文件`/static/jquery.min.js`, `/static/chartkick.js`, `/static/highcharts.js`


运行`ChartServer`模块当我们请求 `/percent/广州/10`这个url的时候，就会执行`job_percent_for_city`方法，然后返回渲染后的文本输出到浏览器

## 四、总结
本文主要记录了爬取的一些要点和过程，更多细节直接看代码

## 五、参考链接
* [Flask的中文介绍](http://docs.jinkan.org/docs/flask/)
* [chartkick+flask画报表](http://www.361way.com/chartkick-flask/4477.html)
* [chartkick.py项目](https://github.com/mher/chartkick.py)
