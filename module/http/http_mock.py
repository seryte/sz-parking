from .http import HttpABC
import json

class HttpMock(HttpABC):
    def __init__(self, retry=0, retry_wait_tm_ms=0.1, cus_logger=None, mock_file="./tests/mock.json"):
        with open(mock_file, "r") as f:
            data = f.read()
            self.response = json.loads(data)

    def make_request(self, url, body=None, headers=None, debug=False):
        if self.response.get(url):
            return json.loads(self.response.get(url))
        return {'msg': 'not found url', "code": -1}