<div align=center>
<img src="https://github.com/RyanChen1997/sz-parking/blob/main/static/logo.png" width="180" height="180"> 
</div>
<br>
<div align=center>
<img alt="Static Badge" src="https://img.shields.io/badge/Python-3.10-blue">
<img alt="Static Badge" src="https://img.shields.io/badge/Email-yongxiangchen69%40gmail.com-8A2BE2?style=plastic&logo=amazonsimpleemailservice&logoColor=white">
<img alt="Static Badge" src="https://img.shields.io/badge/MacOS-green">
<img alt="Static Badge" src="https://img.shields.io/badge/QQ-1009569931-white?logo=qq">
<img alt="Static Badge" src="https://img.shields.io/badge/Email-yongxiangchen69.gmail.com-8A2BE2?logo=amazonsimpleemailservice">
</div>



# 介绍
一个预约深圳公园停车场的小工具，在**深i公园**小程序和**美丽深圳**公众号上面查得到的公园，都可以预约。

# 支持的功能
1. 自动识别和提交数字验证码；
2. 预约成功后车位有效期1个小时；
3. 可调整最长等待时间。

# 运行环境
1. python3.10
2. MacOS（我自己上mac电脑，其他系统应该也行，但是没有测试过）

# 怎么用？
`git clone https://github.com/RyanChen1997/sz-parking.git` 

`cd sz-parking`

`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

`python main.py -h`
```
arking Reservation Tool

options:
  -h, --help            show this help message and exit
  --oneid ONEID         One ID
  --authorization AUTHORIZATION
                        Authorization token
  --xtoken XTOKEN       X Token
  --cookie COOKIE       Cookie
  --auth AUTH           Auth
  --source SOURCE       Source
  --park PARK           Park name
  --parkname PARKNAME   Parking lot name
  --carno CARNO         Car number
  --phone PHONE         Phone number
  --duration_min DURATION_MIN
                        Duration in minutes
```

`python main.py --oneid {one_id} --authorization {authorization} --xtoken {x-token} --cookie {cookie} --source 公众号 --park 深圳湾公园 --parkname 深圳湾公园-日出剧场5号停车场 --carno {车牌号} --phone {手机号}`

需要提供信息：
1. one_id：进入**深i公园**小程序或者**美丽深圳**公众号，抓包获取。
2. authorization：进入**深i公园**小程序或者**美丽深圳**公众号，抓包获取。
3. x-token：进入**深i公园**小程序或者**美丽深圳**公众号，抓包获取。
4. cookie：进入**深i公园**小程序或者**美丽深圳**公众号，抓包获取。
5. source：公众号或者小程序。
6. park：公园名称（在公众号或者小程序中查看）。
7. parkname：公园停车场名称（在公众号或者小程序中查看）。
8. carno：车牌号。
9. phone：手机号。


# 免责声明
仅学习！仅学习！仅学习！请勿商用。

