from abc import abstractmethod, ABC


class HttpABC(ABC):
    @abstractmethod
    def __init__(self, retry=0, retry_wait_tm_ms=0.1, cus_logger=None):
        pass

    @abstractmethod
    def make_request(self, url, body=None, headers=None, debug=False) -> dict:
        pass
