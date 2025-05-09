

# 支持的功能
1. 自动识别和提交数字验证码；
2. 预约成功后有效期1个小时；
3. 可调整最长等待时间。

# 运行环境
1. python3.10
2. MacOS

# 怎么用？
`git clone 此仓库地址` 

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

`python main.py --oneid {one_id} --authorization {authorization} --xtoken {x-token} --cookie {cookie} --source 公众号 --park 公园 --parkname 公园-日出剧场5号 --carno {} --phone {}`

需要提供信息：
1. one_id：，抓包获取。
2. authorization：，抓包获取。
3. x-token：，抓包获取。
4. cookie：，抓包获取。
5. source：公众号或者小程序。
6. park：（在公众号或者小程序中查看）。
7. parkname：（在公众号或者小程序中查看）。
8. carno：车号。
9. phone：手机号。


# 免责声明
仅学习！仅学习！仅学习！请勿商用。

