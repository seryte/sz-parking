import requests
import json
import time
import base64
import execjs
from datetime import datetime
from ocr import ocr_dddd
import random
import utils
from loguru import logger
from typing import List
from module.http import Http, HttpABC

class ParkInfo:
    name: str
    code: str
    id: str

class ParkLot:
    name: str
    code: str
    parks: List[ParkInfo]

class MiniHeaderMeta:
    user_agent = "Mozilla/5.0 (Linux; Android 7.1.2; NX595J Build/NJH47F; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3262 MMWEBSDK/20220105 Mobile Safari/537.36 MMWEBID/323 MicroMessenger/8.0.19.2080(0x28001336) Process/appbrand2 WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wxd44f7a82f424fd40"
    originId = "citypark-mini"

class WechatHeaderMeta:
    user_agent = "Mozilla/5.0 (Linux; Android 14; 23127PN0CC Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260183 MMWEBSDK/20240802 MMWEBID/2374 MicroMessenger/8.0.53.2740(0x2800353A) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
    originId = "gh_95355fb87f0o"

class HTTPParkReservationClient:
    def __init__(
        self,
        one_id,
        token,
        authorization,
        cookie,
        auth,
        source="公众号",
        custom_logger= logger,
        http: HttpABC = None,
    ):
        self._retry = 3  # 每次请求如果失败重试的次数
        self._interval_get_code = 30  # 获取验证码的间隔
        self._last_tm_get_code = None
        self._last_code_value = None
        self._last_book_time = None

        self.one_id = one_id
        self.cookie = cookie
        self.auth = auth
        self.token = token
        self.authorization = authorization
        self.source = source
        self.logger = custom_logger
        self.http = http if http else Http(retry=3, cus_logger=self.logger)

        if self.source == "小程序":
            self.user_agent = MiniHeaderMeta.user_agent
            self.originId = MiniHeaderMeta.originId
        else:
            self.user_agent = WechatHeaderMeta.user_agent
            self.originId = WechatHeaderMeta.originId

    def __gen_timestamp_ms_str(self) -> str:
        return str(round(time.time() * 1000))

    def __get_sign_header_field(self, body, ts):
        body_json = json.dumps(body)

        file_name = "./sign3.js"
        with open(file_name, "r", encoding="UTF-8") as file:
            result = file.read()
        context = execjs.compile(result)
        sign_nonce = context.call("sign", body_json, ts)
        # self.logger.info(sign_nonce)
        sign, nonce = sign_nonce.split("_")
        return nonce, sign

    def __ts_format(self, ts):
        # 把毫秒级时间戳转换成"YYYY-MM-DD HH:MM:SS"的格式
        # 将毫秒级时间戳转换为秒级时间戳
        timestamp_s = float(ts) / 1000.0
        # 使用 datetime 模块将时间戳转换为 datetime 对象
        dt = datetime.fromtimestamp(timestamp_s)
        # 将 datetime 对象格式化为字符串
        formatted_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_dt

    def _get_park_detail(self, park_code="100068", debug=False):
        # 100068是深圳湾公园
        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/parkInfo/parkDetail"

        data = {"parkCode": park_code}
        ts = self.__gen_timestamp_ms_str()
        nonce, sign = self.__get_sign_header_field(data, ts)

        headers = {
            "Host": "smartum.sz.gov.cn",
            "Cookie": self.cookie,
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            "nonce": nonce,
            "x-token": self.token,
            "originid": self.originId,
            "sec-ch-ua-mobile": "?1",
            "authorization": self.authorization,
            "auth": self.auth,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-itemcode": "tcyy",
            "timestamp": ts,
            "user-agent": self.user_agent,
            "x-appcode": "parking",
            "sign": sign,
            "sec-ch-ua-platform": "Android",
            "origin": "https://smartum.sz.gov.cn",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/park-list/100068",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
        }

        return self.http.make_request(url, data, headers, debug)

    def bind_car(self, car_no: str, iphone: str, verification_code: str, debug=False):
        """
        绑定车辆信息到用户账户。

        参数:
        body (dict): 请求体，包含以下键值对：
            - carNo (str): 车牌号，Base64编码后的字符串。
            - carNoType (int): 车牌号类型，1表示普通车牌。
            - iphone (str): 手机号码，Base64编码后的字符串。
            - sourceType (int): 来源类型，1表示某种来源。
            - verificationCode (str): 验证码。
            - oneId (str): 用户唯一标识。

        返回:
        response (requests.Response): HTTP响应对象。
        """

        # return {'code': 0} # mock

        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/userCarInfo/bind"

        if len(utils.parse_base64(car_no)) <= 7:
            car_no_type = 0
        else:
            car_no_type = 1

        body = {
            "carNo": car_no,
            "carNoType": car_no_type,
            "iphone": iphone,
            "sourceType": 1,
            "verificationCode": verification_code,
            "oneId": self.one_id,
        }

        ts = self.__gen_timestamp_ms_str()
        nonce, sign = self.__get_sign_header_field(body, ts)

        headers = {
            "Connection": "keep-alive",
            "Origin": "https://smartum.sz.gov.cn",
            "nonce": nonce,
            "X-token": self.token,
            "originId": self.originId,
            "Authorization": self.authorization,
            "auth": self.auth,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "X-ItemCode": "tcyy",
            "timestamp": ts,
            "User-Agent": self.user_agent,
            "X-AppCode": "parking",
            "sign": sign,
            "Referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/carAdd?iphone=",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Requested-With": "com.tencent.mm",
            "Cookie": self.cookie,
        }

        return self.http.make_request(url, body, headers, debug)

    def search_user_cars(self, debug=False):
        """
        查询用户绑定的车辆信息。

        参数:
        one_id (str): 用户唯一标识。

        返回:
        response (requests.Response): HTTP响应对象。
        """

        # return {'code': 0, 'data': [{'id': '1234567', 'carNo': utils.encode_base64('粤BAJ2620')}]} # mock

        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/userCarInfo/search"

        body = {"oneId": self.one_id}
        ts = self.__gen_timestamp_ms_str()
        nonce, sign = self.__get_sign_header_field(body, ts)

        headers = {
            "Connection": "keep-alive",
            "Origin": "https://smartum.sz.gov.cn",
            "nonce": nonce,
            "X-token": self.token,
            "originId": self.originId,
            "Authorization": self.authorization,
            "auth": self.auth,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "X-ItemCode": "tcyy",
            "timestamp": ts,
            "User-Agent": self.user_agent,
            "X-AppCode": "parking",
            "sign": sign,
            "Referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/carBind",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Requested-With": "com.tencent.mm",
            "Cookie": self.cookie,
        }

        return self.http.make_request(url, body, headers, debug)

    def make_reservation(
        self,
        car_no: str,
        code: str,
        park_code: str,
        phone: str,
        space_id: str,
        verification_code: str,
        line_up_type: int = 0,
        debug=False,
    ):
        """
        预约停车位。

        参数:
        body (dict): 请求体，包含以下键值对：
            - bookTime (str): 预约时间，格式为 "YYYY-MM-DD HH:MM:SS"。
            - carNo (str): 车牌号，Base64编码后的字符串。
            - code (str): 停车场代码。
            - lineUpType (int): 排队类型，0 表示某种排队方式。
            - parkCode (str): 停车场代码。
            - phone (str): 手机号码，Base64编码后的字符串。
            - spaceId (str): 停车位ID。
            - spaceType (int): 停车位类型，0 表示某种类型。
            - verificationCode (str): 验证码。
            - oneId (str): 用户唯一标识。

        返回:
        response (requests.Response): HTTP响应对象。
        """

        # return {"code": 0, 'data': {"reservationNo": "123"}} # mock

        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/app/userReservationApp/reservation"

        if self._last_book_time is None or line_up_type == 0:
            self._last_book_time = self.__gen_timestamp_ms_str()

        ts_format = self.__ts_format(
            str(int(self._last_book_time) + 3600 * 1000)
        )  # 约一个小时

        body = {
            "bookTime": ts_format,
            "carNo": car_no,
            "code": code,
            "lineUpType": line_up_type,
            "parkCode": park_code,
            "phone": phone,
            "spaceId": space_id,
            "spaceType": 0,
            "verificationCode": verification_code,
            "oneId": self.one_id,
        }

        nonce, sign = self.__get_sign_header_field(body, self._last_book_time)

        headers = {
            "Host": "smartum.sz.gov.cn",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            "nonce": nonce,
            "x-token": self.token,
            "originid": self.originId,
            "sec-ch-ua-mobile": "?1",
            "authorization": self.authorization,
            "auth": self.auth,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-itemcode": "tcyy",
            "timestamp": self._last_book_time,
            "user-agent": self.user_agent,
            "x-appcode": "parking",
            "sign": sign,
            "sec-ch-ua-platform": '"Android"',
            "origin": "https://smartum.sz.gov.cn",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/park-booking/100068/p210939824/2574510",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
            "Cookie": self.cookie,
        }

        return self.http.make_request(url, body, headers, debug)
    
    def search_park_lot(self, park_name: str)-> ParkLot: 
        # 分页查询停车场列表。找到park_name
        park_lot = None
        page = 1
        while True:
            response = self._search_parking_lots(page, 10, debug=False)
            if response.get("code") != 0:
                assert RuntimeError(f"search parking lot failed. response={response}")
            park_list = response.get("data", {}).get("list", [])
            if not park_list:
                assert RuntimeError(f"not found parking lot.")
            for item in park_list:
                park_code = item.get("code")
                park_name = item.get("name")
                if park_code and park_name:
                    park_lot = ParkLot()
                    park_lot.name = park_name
                    park_lot.code = park_code
                    break
            if park_lot:
                break
            page += 1
            time.sleep(0.05)
        
        response_detail = self._get_park_detail(
            park_code=park_lot.code, debug=False
        )
        if response_detail.get("code") != 0:
            assert RuntimeError(f"get parking lot detail failed. response={response_detail}")
        lot_list = response_detail.get("data", {}).get("lotList", [])
        parks = []
        for lot in lot_list:
            park = ParkInfo()
            park.name = item.get("name")
            park.id = item.get("id")
            park.code = lot.get("code")
            parks.append(park)
        park_lot.parks = parks
        return park_lot


    def _search_parking_lots(
        self, curr_page: int, page_size: int, park_name: str = "", debug=False
    ):
        """
        查询停车场列表。

        参数:
        curr_page (int): 当前页码。
        page_size (int): 每页显示的记录数。
        park_name (str): 停车场名称，可以为空字符串表示不筛选。

        返回:
        response (requests.Response): HTTP响应对象。
        """
        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/parkInfo/searchList"

        ts = self.__gen_timestamp_ms_str()

        body = {"currPage": curr_page, "pageSize": page_size, "parkName": park_name}

        nonce, sign = self.__get_sign_header_field(body, ts)

        headers = {
            "Host": "smartum.sz.gov.cn",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            "nonce": nonce,
            "x-token": self.token,
            "originid": self.originId,
            "sec-ch-ua-mobile": "?1",
            "authorization": self.authorization,
            "auth": self.auth,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-itemcode": "tcyy",
            "timestamp": ts,
            "user-agent": self.user_agent,
            "x-appcode": "parking",
            "sign": sign,
            "sec-ch-ua-platform": "Android",
            "origin": "https://smartum.sz.gov.cn",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/main",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
            "Cookie": self.cookie,
        }

        return self.http.make_request(url, body, headers, debug)

    def get_code(self, force=False, debug=False):
        """
        获取验证码。

        参数:
        body (dict): 请求体，包含以下键值对：
            - oneId (str): 用户唯一标识。

        返回:
        response (requests.Response): HTTP响应对象。
        """

        # return {"code": 0, "verification_code": '1234'} # mock

        if (
            not force
            and self._last_code_value is not None
            and self._last_tm_get_code is not None
            and time.time() - self._last_tm_get_code < self._interval_get_code
        ):
            return {"code": 0, "verification_code": self._last_code_value}

        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/parkInfo/getCode"

        body = {"oneId": self.one_id}

        ts = self.__gen_timestamp_ms_str()
        nonce, sign = self.__get_sign_header_field(body, ts)

        headers = {
            "Host": "smartum.sz.gov.cn",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            "nonce": nonce,
            "x-token": self.token,
            "originid": self.originId,
            "sec-ch-ua-mobile": "?1",
            "authorization": self.authorization,
            "auth": self.auth,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-itemcode": "tcyy",
            "timestamp": ts,
            "user-agent": self.user_agent,
            "x-appcode": "parking",
            "sign": sign,
            "sec-ch-ua-platform": '"Android"',
            "origin": "https://smartum.sz.gov.cn",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/park-booking/100068/p210939824/2574510",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
            "Cookie": self.cookie,
        }

        data = self.http.make_request(url, body, headers, debug)
        ret = {}

        if data["code"] != 0 or data["msg"] != "TradeOK":
            ret["code"] = data["code"]
            return ret
        img_base64 = data["data"]
        captcha_text = ocr_dddd(img_base64)

        ret["code"] = 0
        ret["verification_code"] = captcha_text

        self._last_tm_get_code = time.time()
        self._last_code_value = captcha_text

        return ret

    def unbind_car(self, car_id: str, phone: str, debug=False):
        """
        解绑用户账户中的车辆信息。

        参数:
        car_id (str): 车辆信息的唯一标识。
        phone (str): 手机号码，Base64编码后的字符串。

        返回:
        response (requests.Response): HTTP响应对象。
        """

        # return {'code': 0} # mock

        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/userCarInfo/unbind"

        body = {
            "id": car_id,
            "oneId": self.one_id,
            "iphone": phone,
        }

        ts = self.__gen_timestamp_ms_str()
        nonce, sign = self.__get_sign_header_field(body, ts)

        headers = {
            "Host": "smartum.sz.gov.cn",
            "User-Agent": self.user_agent,
            "Referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/carBind",
            "Origin": "https://smartum.sz.gov.cn",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Site": "same-origin",
            "nonce": nonce,
            "sign": sign,
            "X-ItemCode": "tcyy",
            "auth": self.auth,
            "timestamp": ts,
            "Authorization": self.authorization,
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "X-AppCode": "parking",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=utf-8",
            "X-token": self.token,
            "originId": self.originId,
            "Sec-Fetch-Mode": "cors",
            "Cookie": self.cookie,
        }

        return self.http.make_request(url, body, headers, debug)

    def search_reservation(self, currPage, pageSize, reservationStatus, debug=False):
        """
        查询用户预约信息。

        参数:
        oneId (str): 用户唯一标识。
        currPage (int): 当前页码。
        pageSize (int): 每页条数。
        reservationStatus (int): 预约状态。

        返回:
        response (requests.Response): HTTP响应对象。
        """
        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/app/userReservationApp/search"

        body = {
            "oneId": self.one_id,
            "currPage": currPage,
            "pageSize": pageSize,
            "reservationStatus": reservationStatus,
        }

        ts = self.__gen_timestamp_ms_str()
        nonce, sign = self.__get_sign_header_field(body, ts)

        headers = {
            "Host": "smartum.sz.gov.cn",
            "Cookie": self.cookie,
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            "nonce": nonce,
            "x-token": self.token,
            "originid": self.originId,
            "sec-ch-ua-mobile": "?1",
            "authorization": self.authorization,
            "auth": self.auth,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-itemcode": "tcyy",
            "timestamp": ts,
            "user-agent": self.user_agent,
            "x-appcode": "parking",
            "sign": sign,
            "sec-ch-ua-platform": '"Android"',
            "origin": "https://smartum.sz.gov.cn",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/bookingRecord?typeVal=0",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
        }

        return self.http.make_request(url, body, headers, debug)

    def cancel_reservation(self, reservation_id, status, debug=False):
        """
        取消用户预约。

        参数:
        reservation_id (int): 预约ID。
        status (int): 预约状态。
        oneId (str): 用户唯一标识。

        返回:
        response (requests.Response): HTTP响应对象。
        """
        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/app/userReservationApp/cancelReservation"

        body = {
            "id": reservation_id,
            "status": status,
            "oneId": self.one_id,
        }

        ts = self.__gen_timestamp_ms_str()
        nonce, sign = self.__get_sign_header_field(body, ts)

        headers = {
            "Host": "smartum.sz.gov.cn",
            "Cookie": self.cookie,
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
            "nonce": nonce,
            "x-token": self.token,
            "originid": self.originId,
            "sec-ch-ua-mobile": "?1",
            "authorization": self.authorization,
            "auth": self.auth,
            "content-type": "application/json;charset=UTF-8",
            "accept": "application/json, text/plain, */*",
            "x-itemcode": "tcyy",
            "timestamp": ts,
            "user-agent": self.user_agent,
            "x-appcode": "parking",
            "sign": sign,
            "sec-ch-ua-platform": '"Android"',
            "origin": "https://smartum.sz.gov.cn",
            "x-requested-with": "com.tencent.mm",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/bookingRecord?typeVal=0",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
        }

        return self.http.make_request(url, body, headers, debug)

    def check_reservation(self, code, park_code, debug=False):
        """
        检查用户预约状态。

        参数:
        code (str): 停车场代码。
        park_code (str): 停车场编号。
        oneId (str): 用户唯一标识。

        返回:
        response (requests.Response): HTTP响应对象。
        """
        url = "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/service-parking-mobile/webapi/app/userReservationApp/checkReservation"

        body = {
            "code": code,
            "parkCode": park_code,
            "oneId": self.one_id,
        }

        ts = self.__gen_timestamp_ms_str()
        nonce, sign = self.__get_sign_header_field(body, ts)

        headers = {
            "Connection": "keep-alive",
            "X-ItemCode": "tcyy",
            "nonce": nonce,
            "X-token": self.token,
            "originId": self.originId,
            "Authorization": self.authorization,
            "auth": self.auth,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "timestamp": ts,
            "User-Agent": self.user_agent,
            "X-AppCode": "parking",
            "sign": sign,
            "Origin": "https://smartum.sz.gov.cn",
            "X-Requested-With": "com.tencent.mm",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/park-list/100068",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": self.cookie,
        }

        return self.http.make_request(url, body, headers, debug)


def encode_base64(value):
    """Helper function to encode strings with Base64."""
    return base64.b64encode(value.encode()).decode()
