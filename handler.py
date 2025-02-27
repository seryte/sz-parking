import client, utils, config
import time
import logging
import random
from loguru import logger


class Handler:
    def __init__(self, one_id, authorization, x_token, cookie, auth, source="", custom_logger=None):
        if custom_logger is None:
            custom_logger = logger
        self.logger = custom_logger
        self.cli = self.__initilize_client(one_id, authorization, x_token, cookie, auth, source, custom_logger)

    def __initilize_client(
        self, one_id, authorization, x_token, cookie, auth, source, logger
    ) -> client.HTTPParkReservationClient:

        cli = client.HTTPParkReservationClient(
            cookie=cookie,
            authorization=authorization,
            token=x_token,
            one_id=one_id,
            auth=auth,
            source=source,
            custom_logger=logger,
        )
        return cli

    def __retry_to_get_code(self, debug=False, retry=3):
        verification_code = ""

        success_get_code = False
        while retry > 0:
            response = self.cli.get_code(force=True, debug=debug)
            if response.get("code") != 0:
                self.logger.info("获取验证码失败")
                return ""
            verification_code = response.get("verification_code", "")
            self.logger.info(f"获取到了验证码{verification_code}")
            if len(verification_code) < 4:
                self.logger.info(f"验证码识别失败, 剩余重试次数: {retry}")
                retry = retry - 1
            else:
                success_get_code = True
                break

        if not success_get_code:
            return ""
        return verification_code

    def get_all_park_names(self):
        all_parks = {}
        page = 1
        while True:
            response = self.cli.search_parking_lots(page, 10, debug=False)
            if response.get("code") != 0:
                break
            park_list = response.get("data", {}).get("list", [])
            if not park_list:
                break
            for item in park_list:
                park_code = item.get("code")
                park_name = item.get("name")
                if park_code and park_name:
                    response_detail = self.cli.get_park_detail(
                        park_code=park_code, debug=False
                    )
                    lot_list = response_detail.get("data", {}).get("lotList", [])
                    lot_names = [lot.get("name") for lot in lot_list if lot.get("name")]
                    all_parks[park_name] = lot_names
                time.sleep(0.05)
            page += 1
        return all_parks

    def search_user_cars(self):
        ret = {}

        response = self.cli.search_user_cars(debug=True)
        if response.get("code") != 0:
            ret["msg"] = response.get("msg")
            ret["code"] = config.FAILED_CODE
            return ret

        ret["code"] = config.SUCCESS_CODE
        ret["msg"] = config.SUCCESS_MSG
        ret["cars"] = []
        data = response.get("data", [])
        for car in data:
            _car_no = utils.parse_base64(car.get("carNo"))
            _phone = utils.parse_base64(car.get("iphone"))
            _car_id = car.get("id")
            ret["cars"].append({"car_no": _car_no, "phone": _phone, "car_id": _car_id})
        return ret

    def search_reservation(self):
        ret = {}

        ret["code"] = config.SUCCESS_CODE
        ret["msg"] = config.SUCCESS_MSG
        ret["reservation_data"] = []
        for status in config.STATUS_RESERVATION:
            response = self.cli.search_reservation(1, 10, status, True)
            if response.get("code") != 0:
                logging.error("查询预约记录失败")
                ret["code"] = config.FAILED_CODE
                ret["msg"] = "查询预约信息失败|" + response.get("msg")
                return ret

            cars = response.get("data", {}).get("list", [])
            if cars is None:
                continue

            for car in cars:
                _car_no = utils.parse_base64(car.get("cardNo"))
                _phone = utils.parse_base64(car.get("phone"))
                _status_str = car.get("reservationStatusStr")
                _id = car.get("id")
                _status = car.get("reservationStatus")
                _reservation_no = car.get("reservationNo")
                _park_name = car.get("parkName")
                _space_name = car.get("spaceName")
                ret["reservation_data"].append(
                    {
                        "car_no": _car_no,
                        "phone": _phone,
                        "status_str": _status_str,
                        "id": _id,
                        "status": _status,
                        "reservation_no": _reservation_no,
                        "park_name": _park_name,
                        "space_name": _space_name,
                    }
                )

        return ret

    def cancel_reservation(self, reservation_data: list, car_no: str = ""):
        ret = {}
        need_cancel_status = ["已预约", "候补中", "待入场"]

        if car_no == "":
            should_cancel = (
                lambda reservation: reservation.get("status_str") in need_cancel_status
            )
        else:
            should_cancel = lambda reservation: reservation.get(
                "status_str"
            ) in need_cancel_status and car_no == reservation.get("car_no")

        for reservation in reservation_data:
            logging.debug(reservation)
            if should_cancel(reservation):
                response = self.cli.cancel_reservation(
                    reservation.get("id"), reservation.get("status")
                )
                if response.get("code") != 0:
                    ret["code"] = config.FAILED_CODE
                    ret["msg"] = response.get("msg")
                    return ret
        ret["code"] = config.SUCCESS_CODE
        ret["msg"] = config.SUCCESS_MSG
        return ret

    def get_park_code(self, park, park_name):
        ret = {}

        park_code = None
        page = 1
        while park_code is None:
            response = self.cli.search_parking_lots(page, 10, debug=True)
            if response.get("code") != 0:
                break
            park_list = response.get("data", {}).get("list", [])
            for item in park_list:
                if item.get("name") == park:
                    park_code = item.get("code")
                    break
            page = page + 1
            if page > 20:
                break
        if park_code is None:
            ret["code"] = config.FAILED_CODE
            ret["msg"] = "获取不到公园"
            return ret

        id = None
        code = None
        response = self.cli.get_park_detail(park_code=park_code, debug=True)
        lot_list = response.get("data", {}).get("lotList", [])
        for lot in lot_list:
            if lot.get("name") == park_name:
                id = lot.get("id")
                code = lot.get("code")
                break

        if id is None or code is None:
            ret["code"] = config.FAILED_CODE
            ret["msg"] = "获取不到停车场"
            return ret

        ret["code"] = config.SUCCESS_CODE
        ret["msg"] = config.SUCCESS_MSG
        ret["park_code"] = park_code
        ret["pcode"] = code
        ret["id"] = id
        return ret

    def unbind_car(self, car_no: str = ""):
        ret = {}

        response = self.search_user_cars()
        if response.get("code") != config.SUCCESS_CODE:
            ret["code"] = config.FAIL_CODE
            ret["msg"] = response.get("msg")
            return
        self.logger.debug(response)

        for car in response.get("cars"):
            if car_no != "" and car.get("car_no") != car_no:
                continue

            car_id = car.get("car_id")
            phone_no_base64 = utils.encode_base64(car.get("phone"))
            response = self.cli.unbind_car(car_id, phone_no_base64, debug=True)
            if response.get("code") != 0:
                ret["code"] = config.FAILED_CODE
                ret["msg"] = "解绑车牌失败|" + response.get("msg")
                return ret

        ret["code"] = config.SUCCESS_CODE
        ret["msg"] = config.SUCCESS_MSG
        return ret

    def bind_car(
        self,
        car_no,
        phone,
    ):
        ret = {}

        verification_code = self.__retry_to_get_code()
        if len(verification_code) < 4:
            ret["code"] = config.FAILED_CODE
            ret["msg"] = "获取验证码失败"
            return ret

        car_no_base64 = utils.encode_base64(car_no)
        phone_base64 = utils.encode_base64(phone)

        response = self.cli.bind_car(
            car_no_base64, phone_base64, verification_code, debug=True
        )
        if (
            response.get("code") != 0
            and response.get("code") != 10013
            and response.get("msg") != "已为您同步更新"
        ):
            ret["code"] = config.FAILED_CODE
            ret["msg"] = "车牌号绑定失败|" + response.get("msg")
            return ret

        ret["code"] = config.SUCCESS_CODE
        ret["msg"] = config.SUCCESS_MSG
        return ret

    def make_reservation(self, park_code, code, id, car_no, phone):
        ret = {}
        car_no_base64 = utils.encode_base64(car_no)
        phone_base64 = utils.encode_base64(phone)

        self.cli.check_reservation(code=code, park_code=park_code, debug=True)

        verification_code = self.__retry_to_get_code()
        if len(verification_code) < 4:
            ret["code"] = config.FAILED_CODE
            ret['msg'] = "获取验证码失败"
            return ret

        self.cli.get_park_detail(park_code=park_code, debug=False)
        self.cli.search_user_cars(debug=False)

        line_up_type = 0
        while True:
            response = self.cli.make_reservation(
                car_no=car_no_base64,
                code=code,
                park_code=park_code,
                phone=phone_base64,
                space_id=id,
                verification_code=verification_code,
                line_up_type=line_up_type,
                debug=True,
            )

            if response.get("code") == 0:
                reservation_no = response.get("data", {}).get("reservationNo", "")
                ret["code"] = config.SUCCESS_CODE
                ret["msg"] = config.SUCCESS_MSG
                ret["reservation_no"] = reservation_no
                ret["line_up_type"] = line_up_type
                return ret

            if "当前车辆已预约" in response.get("msg"):
                ret["code"] = config.SUCCESS_CODE
                ret["msg"] = "当前车辆已预约"
                return ret

            if "候补车位" in response.get("msg"):
                line_up_type = 1
                continue

            ret["code"] = config.FAILED_CODE
            ret["msg"] = "预约失败|" + response.get("msg")
            return ret
    
    def unbind_then_bind(self, car_no, phone):
        unbind_resp = self.unbind_car()
        if unbind_resp.get("code") != config.SUCCESS_CODE:
            return unbind_resp

        self.logger.info("开始绑定车牌")
        response = self.bind_car(car_no=car_no, phone=phone)
        if response.get("code") != config.SUCCESS_CODE:
            self.logger.error(f"绑定车牌失败 {response}")
            return response

        # 查看是否判断成功
        time.sleep(1)
        response = self.search_user_cars()
        for car in response.get("cars"):
            if car.get("car_no") == car_no:
                ret = {}
                ret["code"] = config.SUCCESS_CODE
                ret["msg"] = config.SUCCESS_MSG
                return ret

        ret["code"] = config.FAILED_CODE
        ret["msg"] = "绑定车牌后找不到车牌"
        return ret

    def reserve_until_timeout(self, park, park_name, car_no, phone, duration_min=50):
        # return {"code": config.FAILED_CODE, "msg": "预约失败"}
        ret = {}
        # 检查公园是否存在
        response = self.get_park_code(park, park_name)
        if response.get("code") != config.SUCCESS_CODE:
            ret["code"] = response.get("code")
            ret["msg"] = response.get("msg")
            return ret

        park_code, id, code = response["park_code"], response["id"], response["pcode"]
        self.logger.info(f"获取到了公园的code：park_code: {park_code}, id: {id}, code: {code}")

        # 查询用户的车辆
        response = self.search_user_cars()
        if response.get("code") != config.SUCCESS_CODE:
            ret["code"] = config.FAILED_CODE
            ret["msg"] = "查询用户车辆失败" + response.get("msg")
            return ret
        self.logger.info(f"查询到了用户的车辆信息{response}")

        has_bind = False
        for car in response.get("cars"):
            if car.get("car_no") == car_no:
                has_bind = True
                break
            
        if not has_bind:
            retry = 2 # 重试2次
            err_msg = ""
            while retry > 0:
                retry -= 1
                response = self.unbind_then_bind(car_no=car_no, phone=phone)
                if response.get("code") != config.SUCCESS_CODE:
                    err_msg = response.get('msg')
                    continue
                else:
                    break
            if err_msg != "":
                ret["code"] = config.FAILED_CODE
                ret["msg"] = err_msg
                return ret

        start_time = time.time()
        while True:
            if time.time() - start_time > duration_min * 60:
                ret["code"] = config.FAILED_CODE
                ret["msg"] = "预约时间过长"
                return ret

            time.sleep(float(random.randint(10, 60)) / 100)

            response = self.make_reservation(
                park_code=park_code,
                code=code,
                id=id,
                car_no=car_no,
                phone=phone,
            )
            if response.get("code") == config.SUCCESS_CODE and response.get("msg") == config.SUCCESS_MSG:
                self.logger.info(f"预约成功{response}")
                ret["reservation_no"] = response.get("reservation_no")
                ret["line_up_type"] = response.get("line_up_type")
                ret["code"] = config.SUCCESS_CODE
                ret["msg"] = config.SUCCESS_MSG
                return ret
            elif response.get("msg") == "当前车辆已预约":
                ret["code"] = config.FAILED_CODE
                ret["msg"] = response.get("msg")
                return ret
            else:
                self.logger.info(f"预约失败{response}")

    def run_reservation_task(self, park_code, duration_min=30):
        try:
            start_time = time.time()
            while True:
                if time.time() - start_time > self.data.get("duration", 30) * 60:
                    self.logger.warning("时间到了............")
                    self.task.status = "预约失败"
                    self.task.failed_reason = "预约时间过长"
                    return

                time.sleep(float(random.randint(3, 10)) / 100)

                success = self.__make_reservation(
                    self.data.get("retry_get_code", 3),
                    direct_reserve=True,
                )
                if success:
                    # db.update_user(self.user['id'], reservation_cnt=self.user["reservation_cnt"] + 1)
                    self.task.status = "预约成功"
                    return

        except Exception as e:
            self.logger.error(f"预约异常:{e}")
            self.task.status = "预约失败"
            self.task.failed_reason = "系统异常"


