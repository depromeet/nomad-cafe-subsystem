import json
import time
from dataclasses import field, dataclass

import addr_data_loader
import requests
import cafe
import collector


@dataclass
class CollectorForDaum(collector.Collector):
    data_type: str = "daum"
    headers: dict = field(default_factory=dict)

    def __init__(self, config_map):
        super().__init__(config_map)
        self.headers = {
            "Host": "search.map.daum.net",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/84.0.4147.125 Safari/537.36",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "https://map.kakao.com/?from=total&nil_suggest=btn&q=%EC%97%AD%EC%82%BC%20%EC%B9%B4%ED%8E%98"
                       "&tab=place",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ko,en;q=0.9,en-US;q=0.8,ja;q=0.7"

        }

    def collect(self):
        towns = addr_data_loader.load_seoul_towns()
        total_start = time.time()
        for town in towns:
            start = time.time()
            before_count = self.collect_count
            self._search(f"서울 {town} 카페")
            end = time.time()
            print(f"collected {town}({int(end - start)}s). count : {self.collect_count - before_count}"
                  f", total count : {self.collect_count}")

        end = time.time()
        print(f"finished ({int(end - total_start)}s)")

    def _search(self, query):
        page = 1
        while True:
            objs = self._request_cafe_data(query, page)
            if not objs:
                break

            self.upsert_many(objs)
            page += 1

    def _request_cafe_data(self, query, page):
        url = f"https://search.map.daum.net/mapsearch/map.daum?" \
            f"q={query}&msFlag=A&page={page}&sort=0 "

        cafes = []
        resp = requests.get(url, headers=self.headers)
        query_result = json.loads(resp.text)
        for place in query_result["place"]:
            obj = cafe.Cafe(place["confirmid"], self.data_type, place["name"], place["x"], place["y"])
            obj.parcel_addr = place["address"]
            obj.road_addr = place["new_address"]
            obj.zipcode = place["new_zipcode"]
            obj.homepage = place["homepage"]
            obj.brand_name = place["brandName"]
            obj.phone = place["tel"]
            obj.img = place["img"]
            cafes.append(obj.__dict__)

        return cafes
