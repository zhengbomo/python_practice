#!/usr/bin/python
# -*- coding:utf-8 -*-

from flask_wtf import Form

# 字段类型和字段验证从wtforms导入
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# 表单类继承自Form
class HelloForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

