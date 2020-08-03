import configparser
import http_util


class NaverAPI:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        if "naver" not in config:
            raise Exception("invalid config (not exit naver api setting)")

        temp = dict(config.items("naver"))
        if "url" not in temp:
            raise Exception("invalid config (not exit url)")

        if "client_id" not in temp:
            raise Exception("invalid config (not exit client id)")

        if "client_secret" not in temp:
            raise Exception("invalid config (not exit client secret)")

        self.url = temp["url"]
        self.client_id = temp["client_id"]
        self.client_secret = temp["client_secret"]

    def get(self, start, end):
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
