from module.http import HttpABC, Http, HttpMock
import unittest

class TestHttp(unittest.TestCase):
    def setUp(self):
        self.http: HttpABC
        self.url = "https://httpbin.org/post"

    def test_post(self):
        self.http = Http()
        ret = self.http.make_request(self.url, None, None, True)
        self.assertEqual(ret.get('url'), self.url)
    
    def test_post_with_body_headers(self):
        http = Http()
        body = {"name": "ryan"}
        headers = {"Test-Header": "test"}
        ret = http.make_request(self.url, body, headers, True)
        self.assertEqual(ret.get('json'), body)
        self.assertEqual(ret.get('headers').get('Test-Header'), headers.get('Test-Header'))
    
    def test_post_retry(self):
        self.http = Http(retry=1)
        url = self.url + "test"
        ret = self.http.make_request(url, None, None, True)
        self.assertTrue(ret.get("msg"))
        self.assertTrue("retry=1" in ret.get("msg"))
    
    def test_http_mock(self):
        self.http = HttpMock()
        ret = self.http.make_request(self.url, None, None, True)
        self.assertEqual(ret.get('url'), self.url)

        ret = self.http.make_request("balabla", None, None, True)
        self.assertEqual(ret.get('code'), -1)