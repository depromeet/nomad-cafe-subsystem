import json
import time
from dataclasses import field, dataclass
import openpyxl
import shapefile

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
        towns = self._load_seoul_towns()
        villiges = self._load_seoul_villages()
        v_records = villiges.records()
        v_fields = [x[0] for x in villiges.fields][1:]
        print(v_records)
        print(v_fields)
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

    @staticmethod
    def _load_seoul_towns():
        # 엑셀파일 열기
        wb = openpyxl.load_workbook('national_division.xlsx')
        ws = wb.get_sheet_by_name("2013년")

        towns = []
        for r in ws.rows:
            if r[0].row < 3:    # 1 ~ 2번 라인은 헤더
                continue
            city_code = r[0].value  # 시도코드
            city_name = r[1].value    # 시도명칭
            district_code = r[2].value    # 시군구코드
            district_name = r[3].value   # 시군구명칭
            town_code = r[4].value   # 읍면동코드
            town_name = r[5].value   # 읍면동명칭

            if city_name != "서울특별시":
                continue

            towns.append(town_name)
            print(city_code, city_name, district_code, district_name, town_code, town_name)

        wb.close()
        return towns

    @staticmethod
    def _load_seoul_villages():
        r = shapefile.Reader("LI.shp", encoding="cp949")
        return r

    @staticmethod
    def _load_national_divisions():
        divisions = []
        with open('national_division.json') as json_file:
            obj = json.load(json_file)
            if not obj:
                raise Exception("not exist seoul division data")

            if not obj["features"]:
                raise Exception("not exist seoul division features")

            for feature in obj["features"]:
                if not feature["properties"]:
                    continue
                if not feature["properties"]["name"]:
                    continue
                divisions.append(f"{feature['properties']['name']} 카페")

        return divisions

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
