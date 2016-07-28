#!/usr/bin/python
# -*- coding:utf-8 -*-
import urllib
import urllib2




def add(benjin, lilv, monthadd, month):
    # 月利率
    month_lilv = lilv / 1200.0

    print '7.17: {0}'.format(benjin)

    # 本息
    benxi = benjin * (1 + month_lilv)
    print '8.17: {0}'.format(benxi)

    benxi = (benxi + monthadd) * (1 + month_lilv)
    print '9.17: {0}'.format(benxi)

    benxi = (benxi + monthadd) * (1 + month_lilv)
    print '10.17: {0}'.format(benxi)

    benxi = (benxi + monthadd) * (1 + month_lilv)
    print '11.17: {0}'.format(benxi)

    benxi = (benxi + monthadd) * (1 + month_lilv)
    print '12.17: {0}'.format(benxi)

    benxi = (benxi + monthadd) * (1 + month_lilv)
    print '1.17: {0}'.format(benxi)

    benxi = (benxi + monthadd) * (1 + month_lilv)
    print '2.17: {0}'.format(benxi)

    benxi = (benxi + monthadd) * (1 + month_lilv)
    print '3.17: {0}'.format(benxi)

    benxi = (benxi + monthadd) * (1 + month_lilv)
    print '4.17: {0}'.format(benxi)
    return benxi

print add(16000, 20, 8000, 12)