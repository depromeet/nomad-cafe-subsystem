import configparser
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
        elif self.bot["api_type"] == "seoul_data":
            self.api = seoul_data_api.SeoulDataAPI()
        else:
            raise Exception("invalid api type.", self.bot["api_type"])

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
        while total_count <= start:
            self.api.get(start, start + row_count - 1)
            start += row_count


if __name__ == '__main__':
    bot = CollectBot()
    bot.query(1, 5)
