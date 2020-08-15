import json
import unittest

import db


class DBTest(unittest.TestCase):
    def test_upsert_one(self):
        self.mongo = db.Mongo()
        self.mongo.upsert_one(self.mock())

    def test_upsert_many(self):
        self.mongo = db.Mongo()
        self.mongo.upsert_many([self.mock()])

    def test_find_cafe_in_5km(self):
        self.mongo = db.Mongo()
        cur = self.mongo.find({
            "location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        # 서울특별시 관악구 봉천로 516, 지하1층 (봉천동)
                        "coordinates": [126.95641372307917, 37.48247619555855]
                    },
                    "$maxDistance": 5000
                }
            }
        })

        for c in cur:
            print(c)

    def test_find_cafe_distance(self):
        self.mongo = db.Mongo()
        cur = self.mongo.db.aggregate([
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [126.95641372307917, 37.48247619555855]
                    },
                    # "spherical": "true",
                    "key": "location",
                    "maxDistance": 5000,
                    "distanceField": "dist.calculated",
                    "query": {
                        "road_addr": {"$regex": '^서울'}
                    }
                }
            },
            {"$limit": 5}
        ])

        """
        [결과 예시] 상호명: 도로명주소 (나와의 거리)
            한솔: 서울특별시 관악구 봉천로 516, 지하1층 (봉천동) (0m)
            모도루다방(MODORU DABANG): 서울특별시 관악구 관악로12길 45-9 (봉천동) (176m)
            (주)짜임: 서울특별시 관악구 은천로39길 52, 1층 (봉천동) (946m)
            한독: 서울특별시 관악구 은천로 107, 지하1층 (봉천동) (1095m)
            연화다방: 서울특별시 관악구 쑥고개로 55, 지하1층 (봉천동) (1149m)
        """
        for c in cur:
            print(c)
            print(f'{c["name"]}: {c["road_addr"]} ({int(c["dist"]["calculated"])}m)')

    @staticmethod
    def mock():
        json_str = '{ "_id" : "seoul-data-20", "create_dt" : "2020-08-02T11:09:34.670Z", "data_id" : 20, ' \
                   '"end_hours" : null, "name" : "관악산2호점", "parcel_addr" : "서울특별시 관악구 신림동 210번지 ", "phone" : "02  875 ' \
                   '3448", "road_addr" : "서울특별시 관악구 신림로 23, 1층 (신림동)", "start_hours" : null, "tags" : {  }, ' \
                   '"update_dt" : "2020-08-02T11:09:34.670Z", "x" : "195181.3352", "y" : "440979.1269", ' \
                   '"location" : { "type" : "Point", "coordinates" : [ 126.94628452537923, 37.4709140993146 ] } } '

        return json.loads(json_str)
