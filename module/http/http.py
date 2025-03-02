from loguru import logger
from .http_abs import HttpABC
import requests
import time
import json

class Http(HttpABC):
    def __init__(self, retry=0, retry_wait_tm_ms=0.1, cus_logger=None):
        self.retry = retry
        self.retry_wait_tm_ms = retry_wait_tm_ms
        self.logger = cus_logger if cus_logger else logger
    
    def make_request(self, url, body, headers, debug) -> dict:
        self.logger.info(f"Requesting: {url}")
        retry = self.retry
        while True:
            try:
                response = requests.post(url, json=body, headers=headers)
                if debug:
                    self.logger.info(f"Request Body: {body}")
                    self.logger.info(f"Response: {json.dumps(response.json())}")
                    # self.logger.info(f"Response Headers: {response.headers}")
                return response.json()
            except Exception as e:
                self.logger.error(f"Error making request: {e}")
                if retry > 0:
                    retry = retry - 1
                    self.logger.warning(f"请求失败，剩余{retry}次重试")
                    time.sleep(self.retry_wait_tm_ms)
                    continue
                else:
                    return {"msg": f"error={str(e)}, retry={self.retry-retry}", "code": -1}