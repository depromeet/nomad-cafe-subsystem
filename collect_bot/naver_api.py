import configparser
import http_util


class NaverAPI:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')

        temp = {}
        if "naver" not in config:
            print("invalid config (not exit naver api setting)")
            exit(1)

        for (k, v) in config.items("naver"):
            temp[k] = v

        if "url" not in temp:
            print("invalid config (not exit url)")
            exit(1)

        if "client_id" not in temp:
            print("invalid config (not exit client id)")
            exit(1)

        if "client_secret" not in temp:
            print("invalid config (not exit client secret)")
            exit(1)

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
