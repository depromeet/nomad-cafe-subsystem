import unittest
import geo_util


class GeoUtilTest(unittest.TestCase):
    def test_transform(self):
        # 서울특별시 관악구 봉천로 516
        # 실제 지도에서 확인 결과 위치가 정확히 일치하지 않음. 주소로 좌표를 직접 얻어 오던지 다른 알고리즘 사용 필요
        x = 196078.0075
        y = 442261.8928
        (lat, lon) = geo_util.GeoUtil.transform_location(x, y)
        print(lat, lon)
        self.assertTrue(lat == 37.48247619555855)
        self.assertTrue(lon == 126.95641372307917)


