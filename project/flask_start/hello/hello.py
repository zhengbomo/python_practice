#!/usr/bin/python
# -*- coding:utf-8 -*-

from datetime import datetime

from flask import Flask
from flask import request
from flask import make_response
from flask import abort
from flask import render_template

from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from HelloForm import HelloForm

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# 路由支持动态参数,flask会将动态参数作为函数参数传入
@app.route(u'/user/id/<int:id>')
def user_with_id(id):
    return '<h1>Hello flask! %s </h1>' % id


# 支持声明类型(Flask 支持在路由中使用 int、float 和 path 类型)
@app.route(u'/user/name/<path:name>')
def user_with_name(name):
    return render_template('user.html', name=name)



@app.route('/header')
def request_with_header():
    user_agent = request.headers.get('User-Agent')
    return '<h2>Your browser is </h2> <p>%s</p>' % user_agent


@app.route('/response')
def response():
    return '<h1>Bad Request</h1>', 400


@app.route('/makeresponse')
def make_resp():
    resp = make_response('<h1>This document carries a cookie!</h1>')
    resp.set_cookie('answer', '42')
    return resp


@app.route('/redirect')
def redirect():
    return redirect('http://www.example.com')


@app.route('/404')
def notfound():
    return abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/utctime')
def utctime():
    return render_template('utctime.html', current_time=datetime.utcnow())


@app.route('/form', methods=['GET', 'POST'])
def hello_form():
    name = None
    form = HelloForm()
    # 判断是否是submit提交的表单
    if form.validate_on_submit():
        name = form.name.data
    return render_template('helloform.html', form=form, name=name)


# 如果是入口模块,启动服务
if __name__ == '__main__':
    app.debug = True
    app.config['SECRET_KEY'] = 'hard to guess string'

    bootstrap = Bootstrap(app)
    moment = Moment(app)
    manager = Manager(app)
    manager.run()
