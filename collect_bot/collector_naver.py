import datetime

import collector
import http_util
import cafe


class CollectorForNaver(collector.Collector):
    def __init__(self, config_map):
        super().__init__(config_map)
        if "naver" not in self.config_map:
            raise Exception("invalid config (not exit naver api setting)")

        if "url" not in self.config_map["naver"]:
            raise Exception("invalid config (not exit url)")

        if "client_id" not in self.config_map["naver"]:
            raise Exception("invalid config (not exit client id)")

        if "client_secret" not in self.config_map["naver"]:
            raise Exception("invalid config (not exit client secret)")

        self.url = self.config_map["naver"]["url"]
        self.client_id = self.config_map["naver"]["client_id"]
        self.client_secret = self.config_map["naver"]["client_secret"]
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
        if "total" not in resp:
            raise Exception("not exist key(total)")

        return resp["total"]

    def _get(self, start, end):
        params = {
            'query': "카페".encode("utf-8"),
            'display': end - start,  # max=5
            'start': start,  # 검색 시작 포인트
            'sort': 'random'  # random 일 경우 유사도순
        }

        return http_util.HTTPUtil.get(self.url, params=params, headers={
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret,
        })

    def _parse(self, resp):
        datas = []
        for data in resp["items"]:
            try:
                obj = cafe.Cafe(
                    data_id=self.collect_count,
                    data_type=self.data_type,
                    name=data["title"],
                    parcel_addr=data["address"],
                    road_addr=data["roadAddress"],
                    phone=data["telephone"],
                    x=data["mapx"],
                    y=data["mapy"],
                    create_dt=datetime.datetime.utcnow(),
                    update_dt=datetime.datetime.utcnow())
                datas.append(obj.__dict__)
            except Exception as e:
                print(e)

        return datas
