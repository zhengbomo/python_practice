#!/usr/bin/python
# -*- coding:utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date, Boolean

Base = declarative_base()


class MyLoan(Base):
    __tablename__ = 'my_loan'

    def __init__(self):
        self.id = Column(Integer, primary_key=True)
        self.create_date = Column(Date)
        self.normal_lilv = Column(Float)
        self.finished_lilv = Column(Float)
        self.unfinished_lilv == Column(Float)
        self.total_buy = Column(Float)

