import unittest
from module.client import HTTPParkReservationClient


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = HTTPParkReservationClient(
            one_id="",
            token="",
            auth="",
            authorization="",
            cookie=""
        )

    def test_search_park(self):
        park_lot = self.client.search_park_lot("深圳湾公园")
        self.assertEqual(park_lot.name, "深圳湾公园")
        self.assertEqual(park_lot.code, '100068')
        self.assertGreater(len(park_lot.parks), 0)

    def test_get_user_cars(self):
        cars = self.user.get_user_cars()
        self.assertGreater(len(cars), 0)
        self.assertEqual(cars[0].car_no, "粤A12345")

    def test_get_reservations(self):
        reservations = self.client.get_reservations()
        self.assertGreater(len(reservations), 0)
        self.assertEqual(reservations[0].reservation_no, "1234567890")

    def test_cancel_reservation(self):
        car = Car(car_no="粤A12345")
        self.client.cancel_reservation(car)

    def test_unbind_car(self):
        car = Car(car_no="粤A12345")
        self.client.unbind_car(car)
    
    def test_get_verification_code(self):
        code = self.client.get_verification_code()
        # 断言code是一个4个数字的字符串
        self.assertTrue(code.isdigit() and len(code) == 4)

    def test_reservation(self):
        pass

if __name__ == "__main__":
    unittest.main()
