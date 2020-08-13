import unittest
import seoul_data_api


class SeoulDataAPITest(unittest.TestCase):
    def test_get(self):
        api = seoul_data_api.SeoulDataAPI()
        resp = api.get(1, 5)
        self.assertTrue("coffeeShopInfo" in resp)
        self.assertTrue("RESULT" in resp["coffeeShopInfo"])
        self.assertTrue("CODE" in resp["coffeeShopInfo"]["RESULT"])
        self.assertTrue(resp["coffeeShopInfo"]["RESULT"]["CODE"] == "INFO-000")
        self.assertTrue(len(resp["coffeeShopInfo"]["row"]) == 5)

