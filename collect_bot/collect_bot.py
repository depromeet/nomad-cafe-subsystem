import configparser
import naver_api


class CollectBot:
    """
    지역별 카페 정보를 수집하는 봇
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        self.bot = {}
        if "bot" not in config:
            print("invalid config (not exit bot setting)")
            exit(1)

        for (k, v) in config.items("bot"):
            self.bot[k] = v

        if "api_type" not in self.bot:
            print("invalid config (not exit api setting)")
            exit(1)

        if self.bot["api_type"] == "naver":
            self.api = naver_api.NaverAPI()
        elif self.bot["api_type"] == "seoul_data":
            self.api = {}
        else:
            print("invalid api type.", self.bot["api_type"])
            exit(1)

    def query(self, query_string, start):
        self.api.get(query_string, start)


if __name__ == '__main__':
    bot = CollectBot()
    bot.query('카페', 1000)
