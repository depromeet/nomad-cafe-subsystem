import concurrent.futures
import datetime
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import field, dataclass

import addr_data_loader
import cafe
import collector
import requests
import runner
import tqdm


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
        self.addr_loader = addr_data_loader.AddrDataLoader()
        self.runner = runner.Runner()
        self.locks = {}
        self.progress_bar = {}
        self.progress_count = 0
        self.progress_lock = threading.Lock()
        self.completes = []

    def collect(self):
        villiges = self.addr_loader.load_villiges_from_addr_api()
        towns = self.addr_loader.load_towns_from_addr_api()

        self.progress_bar = tqdm.tqdm(total=len(towns), desc="카페 정보 수집 중")
        try:
            thread_count = 50
            thread_list = []
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                for town in towns:
                    thread_list.append(executor.submit(self.search, {
                        "town": town,
                        "villiges": villiges[town]
                    }))

                for execution in concurrent.futures.as_completed(thread_list):
                    execution.result()
        except Exception as e:
            print(e)
        finally:
            print(f"complete. {self.completes}")

    def search(self, data):
        town = data["town"]
        villiges = data["villiges"]
        if town == "가양2동":
            print(town)

        for villige in villiges:
            cafes = []
            page = 1
            while True:
                objs = self._request_cafe_data(f"{villige} 카페", page)
                if not objs:  # 한 페이지 당 최대 카페수는 15
                    break

                cafes.extend(objs)

                if len(objs) < 15:  # 한 페이지 당 최대 카페수는 15
                    break

                page += 1
                time.sleep(1)

            if cafes:
                self.upsert_many(cafes)
            # self._append_to_file(town, cafes)
            # print(f"collected {villige}")

        self.completes.append(town)
        self._update_progress()

    def _request_cafe_data(self, query, page):
        url = f"https://search.map.daum.net/mapsearch/map.daum?" \
            f"q={query}&msFlag=A&page={page}&sort=0 "

        cafes = []
        resp = requests.get(url, headers=self.headers)
        query_result = json.loads(resp.text)
        required_category = ["카페", "커피전문점"]
        for place in query_result["place"]:
            confirmid = self.getStrSafety(place, "confirmid")
            name = self.getStrSafety(place, "name")
            x = self.getStrSafety(place, "x")
            y = self.getStrSafety(place, "y")

            obj = cafe.Cafe(confirmid, self.data_type, name, x, y)
            depth = self.getStrSafety(place, "last_cate_depth")
            if depth:
                try:
                    cate_depth = int(depth)
                    for i in range(0, cate_depth):
                        cate_name = self.getStrSafety(place, f"cate_name_depth{i+1}")
                        obj.cate_names.append(cate_name)
                except Exception as e:
                    print(e)

            is_valid = any(elem in obj.cate_names for elem in required_category)
            if not is_valid:
                continue

            obj.parcel_addr = self.getStrSafety(place, "address")
            obj.road_addr = self.getStrSafety(place, "new_address")
            obj.zipcode = self.getStrSafety(place, "new_zipcode")
            obj.homepage = self.getStrSafety(place, "homepage")
            obj.brand_name = self.getStrSafety(place, "brandName")
            obj.phone = self.getStrSafety(place, "tel")
            obj.img = self.getStrSafety(place, "img")

            obj.addinfo_appointment = self.getStrSafety(place, "addinfo_appointment")
            obj.addinfo_wifi = self.getStrSafety(place, "addinfo_wifi")
            obj.addinfo_delivery = self.getStrSafety(place, "addinfo_delivery")
            obj.addinfo_pet = self.getStrSafety(place, "addinfo_pet")
            obj.addinfo_nursery = self.getStrSafety(place, "addinfo_nursery")
            obj.addinfo_fordisabled = self.getStrSafety(place, "addinfo_fordisabled")
            obj.addinfo_package = self.getStrSafety(place, "addinfo_package")
            obj.addinfo_parking = self.getStrSafety(place, "addinfo_parking")
            obj.addinfo_smokingroom = self.getStrSafety(place, "addinfo_smokingroom")

            obj.last_cate_id = self.getStrSafety(place, "last_cate_id")
            obj.last_cate_name = self.getStrSafety(place, "last_cate_name")
            obj.last_cate_name = self.getStrSafety(place, "test")

            cafes.append(obj.__dict__)

        return cafes
    
    @staticmethod
    def getStrSafety(obj, key):
        if key in obj:
            return obj[key]
        else:
            return ""

    # 수집한 데이터는 json 파일로 저장
    def _append_to_file(self, town, datas):
        if town not in self.locks:
            self.locks[town] = threading.Lock()

        lock = self.locks[town]
        lock.acquire()
        with open(f"data/{town}.json", 'a', encoding="utf-8") as f:
            if datas:
                for data in datas:
                    f.write(json.dumps(data, ensure_ascii=False, default=self.json_default) + ",")

        lock.release()

    @staticmethod
    def json_default(value):
        if isinstance(value, datetime.date):
            return value.strftime('%c')
        raise TypeError('not JSON serializable')

    def _update_progress(self):
        self.progress_lock.acquire()
        self.progress_bar.update(1)
        self.progress_lock.release()
