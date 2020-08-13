import datetime

import cafe
import collector
import http_util


class CollectorForSeoulData(collector.Collector):
    def __init__(self, config_map):
        super().__init__(config_map)

        if "seoul_data" not in self.config_map:
            raise Exception("invalid config (not exit seoul data setting)")

        config_key_groups = ['url', 'key']
        for key in config_key_groups:
            if key not in self.config_map["seoul_data"]:
                raise Exception(f"invalid config (not exit {key}")

        self.url = self.config_map["seoul_data"]["url"]
        self.key = self.config_map["seoul_data"]["key"]
        self.data_type = self.config_map["bot"]["api_type"]

    def collect(self):
        total_count = self._get_total_count()
        start = 1
        row_count = 100
        while start <= total_count:
            resp = self._get(start, start + row_count - 1)
            start += row_count
            objs = self._parse(resp)
            if objs:
                self.upsert_many(objs)

    def _get_total_count(self):
        resp = self._get(start=1, end=2)
        if "list_total_count" not in resp:
            raise Exception("not exist key(list_total_count)")

        return resp["list_total_count"]

    def _get(self, start, end):
        resp = http_util.HTTPUtil.get(f"{self.url}/{self.key}/json/coffeeShopInfo/{start}/{end}/")
        if "coffeeShopInfo" not in resp:
            raise Exception("not exist key (coffeeShopInfo)")

        if "RESULT" not in resp["coffeeShopInfo"]:
            raise Exception("not exist key (RESULT)")

        if resp["coffeeShopInfo"]["RESULT"]["CODE"] != "INFO-000":
            raise Exception(resp["coffeeShopInfo"]["RESULT"]["MESSAGE"])

        return resp["coffeeShopInfo"]

    def _parse(self, resp):
        datas = []
        for data in resp["row"]:
            try:
                obj = cafe.Cafe(
                    data_id=int(data["ID"]),
                    data_type=self.data_type,
                    name=data["NM"],
                    parcel_addr=data["ADDR_OLD"],
                    road_addr=data["ADDR"],
                    phone=data["TEL"],
                    x=data["XCODE"],
                    y=data["YCODE"],
                    create_dt=datetime.datetime.utcnow(),
                    update_dt=datetime.datetime.utcnow())
                datas.append(obj.__dict__)
            except Exception as e:
                print(e)

        return datas
