#!/usr/bin/python
# -*- coding:utf-8 -*-

# 1. 统计不同文化的人的借款人数
sql = u'select wenhua, count(*) count from userinfo group by wenhua'

# 2. 统计不同文化的人中
sql = u'select wenhua, avg(`total_borrow_amount`) total_borrow_amount from userinfo group by wenhua'

# 3. 统计已婚和未婚的人,借款数
sql = 'select jiehun, FORMAT(avg(total_borrow_amount), 0) total_borrow from userinfo group by jiehun order by ' \
      'total_borrow '

# 4. 统计不同年龄段的人
sql = """
select nnd, count(*) as '人数' from
(
select
case
when age>=1 and age<=10 then '1-10'
when age>=11 and age<=20 then '11-20'
when age>=21 and age<=30 then '21-30'
when age>=31 and age<=40 then '31-40'
when age>=41 and age<=50 then '41-50'
when age>=51 and age<=60 then '51-60'
when age>=60 then '60+'
end
as nnd, username from userinfo
) userinfo
group by nnd
"""

# 5. 统计不同

# 5 提前还款排名前10的用户的信息
sql = """
select * from (
	select * from userinfo order by tiqian_days limit 10
) as t
"""

# 前10名:总借款额平均为5405
# 前20名:总借款额平均为5505


