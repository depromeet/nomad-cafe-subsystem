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

    def query(self, query_string, start):
        self.api.get(query_string, start)


if __name__ == '__main__':
    bot = CollectBot()
    bot.query(1, 5)
