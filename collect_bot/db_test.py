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

    @staticmethod
    def mock():
        json_str = '{ "_id" : "seoul-data-20", "create_dt" : "2020-08-02T11:09:34.670Z", "data_id" : 20, ' \
                   '"end_hours" : null, "name" : "관악산2호점", "parcel_addr" : "서울특별시 관악구 신림동 210번지 ", "phone" : "02  875 ' \
                   '3448", "road_addr" : "서울특별시 관악구 신림로 23, 1층 (신림동)", "start_hours" : null, "tags" : {  }, ' \
                   '"update_dt" : "2020-08-02T11:09:34.670Z", "x" : "195181.3352", "y" : "440979.1269", ' \
                   '"location" : { "type" : "Point", "coordinates" : [ 126.94628452537923, 37.4709140993146 ] } } '

        return json.loads(json_str)

