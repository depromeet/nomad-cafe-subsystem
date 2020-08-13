import configparser
import json
import time

import collector
import http_util
import addr_data_loader


class CollectorAddr(collector.Collector):
    def __init__(self, config_map):
        super().__init__(config_map)
        if "addr_key" not in self.config_map["bot"]:
            raise Exception("invalid config (not exit addr key)")

        self.addr_url = self.config_map["bot"]["addr_url"]
        self.addr_key = self.config_map["bot"]["addr_key"]

    def collect(self):
        towns = addr_data_loader.load_seoul_towns()
        for town in towns:
            if town == "천호동":
                continue

            self.collect_by_town(town)

    def collect_by_town(self, town):
        result = []
        total_count = self._get_total_count(town)
        curr_page = 1
        row_count = 100
        loop_count = total_count / row_count + 1
        total_start = time.time()
        while curr_page <= loop_count:
            start = time.time()
            resp = self._get(curr_page, row_count, town)
            if resp["results"]["common"]["errorCode"] != "0":
                break

            objs = self._parse(resp)
            result.extend(objs)
            result = list(set(result))
            end = time.time()
            print(f"page {curr_page} collected ({int(end - start)}s). count : {len(objs)}")
            curr_page += 1

        end = time.time()
        print(f"collected {town}({int(end - total_start)}s). count : {len(result)}"
              f", total count : {self.collect_count}")
        self.append_to_file({town: result})

    @staticmethod
    def append_to_file(data):
        with open("juso.txt", 'a', encoding="utf-8") as f:
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
    CollectorAddr(config_map).collect()
