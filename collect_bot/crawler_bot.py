import json
from dataclasses import field, dataclass

import requests
import cafe


@dataclass
class CrawlerBot:
    """
    API로 가져올 수 없는 데이터를 크롤링하기 위한 봇
    """
    collect_count: int = 0
    data_type: str = "daum"
    headers: dict = field(default_factory=dict)

    def __init__(self):
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

    def crawling(self, query):
        page = 1
        while True:
            cafes = self.search(query, page)
            if not cafes:
                break

            self.save(cafes)
            page += 1

    def search(self, query, page):
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
            cafes.append(obj)

        return cafes

    def save(self, cafes):
        self.db.upsert_many(cafes)
        self.collect_count += cafes.__len__()
        print(f"current count : {self.collect_count}")


if __name__ == "__main__":
    bot = CrawlerBot()
    bot.crawling("역삼 카페", 1)
