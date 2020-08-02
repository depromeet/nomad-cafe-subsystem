import configparser
import cafe_factory
import db
import naver_api
import seoul_data_api


class CollectBot:
    """
    지역별 카페 정보를 수집하는 봇
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        self.bot = {}
        if "bot" not in config:
            raise Exception("invalid config (not exit bot setting)")

        for (k, v) in config.items("bot"):
            self.bot[k] = v

        config_key_groups = ['api_type', 'db_type']
        for key in config_key_groups:
            if key not in self.bot:
                raise Exception(f"invalid config (not exit {key}")

        if self.bot["api_type"] == "naver":
            self.api = naver_api.NaverAPI()
        elif self.bot["api_type"] == "seoul-data":
            self.api = seoul_data_api.SeoulDataAPI()
        else:
            raise Exception("invalid api type.", self.bot["api_type"])

        if self.bot["db_type"] == "mongo":
            self.db = db.Mongo()
        else:
            raise Exception("invalid db type.", self.bot["db_type"])

    def query(self, start, end):
        self.api.get(start, end)

    def get_total_count(self):
        resp = self.api.get(start=1, end=1)
        if "list_total_count" not in resp:
            raise Exception("not exist key(list_total_count)")

        return resp["list_total_count"]

    def collect(self):
        total_count = self.get_total_count()
        start = 1
        row_count = 100
        while start <= total_count:
            resp = self.api.get(start, start + row_count - 1)
            start += row_count
            self.save(resp)

    def save(self, resp):
        datas = []
        data_type = self.bot["api_type"]
        for data in resp["row"]:
            try:
                obj = cafe_factory.CafeFactory().new_cafe(data_type, data)
                datas.append(obj.__dict__)
            except Exception as e:
                print(e)

        if len(datas) > 0:
            self.db.upsert_many(datas)


if __name__ == '__main__':
    bot = CollectBot()
    bot.collect()
