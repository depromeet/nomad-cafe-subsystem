import concurrent
import configparser
import json
import time
from concurrent.futures.thread import ThreadPoolExecutor

import addr_data_loader
import collector
import http_util
import runner
import tqdm
import util


class CollectorAddr(collector.Collector):
    """
    동 이름으로 하위 도로명 조회 후 파일로 저장
    """

    def __init__(self, config_map):
        super().__init__(config_map)
        if "addr_key" not in self.config_map["bot"]:
            raise Exception("invalid config (not exit addr key)")

        if "url" not in self.config_map["kakao"]:
            raise Exception("invalid config (not exit url)")

        if "key" not in self.config_map["kakao"]:
            raise Exception("invalid config (not exit key)")

        self.addr_loader = addr_data_loader.AddrDataLoader()
        self.runner = runner.Runner()
        self.addr_url = self.config_map["bot"]["addr_url"]
        self.addr_key = self.config_map["bot"]["addr_key"]
        self.progress_bar = {}
        self.kakao_addr_api_url = self.config_map["kakao"]["url"]
        self.kakao_addr_api_key = self.config_map["kakao"]["key"]

    # 데이터 수집 시작
    def collect(self):
        towns = self.addr_loader.load_seoul_towns_from_xlsx()
        already_exist_towns = self.addr_loader.load_towns_from_addr_api()
        target_towns = util.excloud_exist_data_for_array(towns, already_exist_towns)
        print(f"total towns : {len(towns)}, after remove exist count : {len(target_towns)}\n")

        self.runner.run(self.collect_by_towns, target_towns)

    def collect_by_towns(self, towns):
        print(f"다음 동들의 도로명 수집 : {towns}")
        for town in towns:
            print(f"{town} 도로명 수집 시작\n")
            self.collect_by_town(town)

    def collect_by_town(self, town):
        result = []
        total_count = self._get_total_count(town)
        curr_page = 1
        row_count = 100
        loop_count = total_count / row_count + 1
        total_start = time.time()

        progress_bar = tqdm.tqdm(total=total_count, desc=town)
        while curr_page <= loop_count:
            resp = self._get(curr_page, row_count, town)
            if resp["results"]["common"]["errorCode"] != "0":
                break

            objs = self._parse(resp)
            result.extend(objs)
            result = list(set(result))
            curr_page += 1
            progress_bar.update(row_count)
            break

        progress_bar.close()
        end = time.time()
        print(f"collected {town}({int(end - total_start)}s). count : {len(result)}"
              f", total count : {self.collect_count}")
        self.append_to_file({town: result})

    def convert_wcongnamul_to_wgs84(self):
        """
        daum의 좌표계로 사용되는 wcongnamul 좌표를 wgs84(lat, lon) 형식으로 변환
        """
        thread_datas = []
        i = 1
        print("데이터베이스에서 데이터 로드 중")
        while True:
            data = self.skiplimit(page_size=1000, page_num=i)
            if not data:
                break

            thread_datas.append(data)
            i += 1

        print("데이터 로드 완료")

        total_count = 0
        for datas in thread_datas:
            total_count += len(datas)

        self.progress_bar = tqdm.tqdm(total=total_count, desc="좌표 변환 중")
        try:
            thread_count = 4
            thread_list = []
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                for data in thread_datas:
                    thread_list.append(executor.submit(self.convert, data))

                for execution in concurrent.futures.as_completed(thread_list):
                    execution.result()
        except Exception as e:
            print(e)

    def convert(self, datas):
        for data in datas:
            try:
                obj = self._get_addr_info(data["road_addr"])
                if not obj:
                    continue

                data["location"]["coordinates"] = [float(obj["x"]), float(obj["y"])]

                if "road_address" in obj:
                    ra = obj["road_address"]
                    data["region_1depth_name"] = ra["region_1depth_name"]
                    data["region_2depth_name"] = ra["region_2depth_name"]
                    data["region_3depth_name"] = ra["region_3depth_name"]
                    data["road_name"] = ra["road_name"]

                self.get_db().update_one({
                    "_id": data["_id"]
                }, {
                    "$set": data
                })
                self.progress_bar.update(1)
            except Exception as e:
                print(f"fail. {data}, err : {e}")

    def _get_addr_info(self, query):
        headers = {
            "Authorization": f"KakaoAK {self.kakao_addr_api_key}"
        }

        resp = http_util.HTTPUtil.get(f"{self.kakao_addr_api_url}?page=1&AddressSize=1&query='{query}'",
                                      headers=headers)
        if "documents" not in resp:
            print(f"err : not exist data {query}")
            return {}

        if not resp["documents"]:
            return {}

        return resp["documents"][0]

    def skiplimit(self, page_size, page_num):
        # Calculate number of documents to skip
        skips = page_size * (page_num - 1)

        # Skip and limit
        cursor = self.get_db().find().skip(skips).limit(page_size)

        # Return documents
        return [x for x in cursor]

    def get_db(self):
        return self.db.db

    # 수집한 데이터는 json 파일로 저장
    @staticmethod
    def append_to_file(data):
        with open("juso.json", 'a', encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + ",")

    def _get_total_count(self, keyword):
        resp = self._get(start=1, count=2, keyword=keyword)
        return int(resp["results"]["common"]["totalCount"])

    def _get(self, start, count, keyword):
        params = {
            'confmKey': self.addr_key,
            'currentPage': start,
            'countPerPage': count,  # 페이지당 주소 수
            'keyword': keyword,
            'resultType': "json",
        }

        resp = http_util.HTTPUtil.get(self.addr_url, params=params)
        if "results" not in resp:
            raise Exception("not exist key(results)")

        if "common" not in resp["results"]:
            raise Exception("not exist key(common)")

        if "juso" not in resp["results"]:
            resp["results"]["juso"] = []

        return resp

    @staticmethod
    def _parse(resp):
        datas = []
        for juso in resp["results"]["juso"]:
            datas.append(juso["rn"])

        return datas


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('collect_bot.ini')
    config_map = {}
    for key in config.keys():
        config_map[key] = dict(config.items(key))

    addr = CollectorAddr(config_map)
    # 모든 도로명 수집
    # CollectorAddr(config_map).collect()

    # 몽고디비에서 페이징 처리해서 데이터 가져오기
    r = addr.skiplimit(page_size=1000, page_num=10)

    # 좌표 변환
    addr.convert_wcongnamul_to_wgs84()
