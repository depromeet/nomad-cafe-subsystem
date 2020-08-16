import concurrent
import configparser
from concurrent.futures.thread import ThreadPoolExecutor

import addr_data_loader
import db
import http_util
import runner
import tqdm


class ConvertCoordinate:
    """
    데이터베이스에 저장된 도로명 주소로 좌표 정보 검색 후 업데이트
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('collect_bot.ini')
        config_map = {}
        for key in config.keys():
            config_map[key] = dict(config.items(key))

        if config_map["bot"]["db_type"] == "mongo":
            self.db = db.Mongo()
        else:
            raise Exception("invalid db type.", config_map["bot"]["db_type"])

        if "url" not in config_map["kakao"]:
            raise Exception("invalid config (not exit url)")

        if "key" not in config_map["kakao"]:
            raise Exception("invalid config (not exit key)")

        self.addr_loader = addr_data_loader.AddrDataLoader()
        self.runner = runner.Runner()
        self.progress_bar = {}
        self.kakao_addr_api_url = config_map["kakao"]["url"]
        self.kakao_addr_api_key = config_map["kakao"]["key"]

    def convert_wcongnamul_to_wgs84(self):
        """
        daum의 좌표계로 사용되는 wcongnamul 좌표를 wgs84(lat, lon) 형식으로 변환
        """
        thread_datas = self._load_cafes_from_db()

        total_count = 0
        for datas in thread_datas:
            total_count += len(datas)

        self.progress_bar = tqdm.tqdm(total=total_count, desc="좌표 변환 중")
        try:
            thread_count = 4
            thread_list = []
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                for data in thread_datas:
                    thread_list.append(executor.submit(self._convert, data))

                for execution in concurrent.futures.as_completed(thread_list):
                    execution.result()
        except Exception as e:
            print(e)

    def _load_cafes_from_db(self):
        """
        데이터베이스에서 카페 정보를 1000개씩 나눠서 배열에 저장 (스레드 처리하기 위함)
        :return: 카페 정보를 1000개씩 나눠 담은 배열
        """
        datas = []
        i = 1
        print("데이터베이스에서 데이터 로드 중")
        while True:
            data = self._find_per_page_from_db(page_size=1000, page_num=i)
            if not data:
                break

            datas.append(data)
            i += 1

        print("데이터 로드 완료")
        return datas

    def _convert(self, cafes):
        """
        데이터베이스에 저장된 데이터들의 좌표 정보를 조회하여 기존의 wcongnamul 좌표체계에서 wgs84 좌표 체계로 변환
        :param cafes: 데이터베이스에 저장된 카페 정보 목록
        :return:
        """
        for data in cafes:
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

                self.db.update_one({
                    "_id": data["_id"]
                }, {
                    "$set": data
                })
                self.progress_bar.update(1)
            except Exception as e:
                print(f"fail. {data}, err : {e}")

    def _get_addr_info(self, road_addr):
        """
        도로명 주소 좌표 정보 조회
        :param road_addr: 도로명 주소
        :return: 도로명 주소에 대한 좌표 정보
        """
        headers = {
            "Authorization": f"KakaoAK {self.kakao_addr_api_key}"
        }

        resp = http_util.HTTPUtil.get(f"{self.kakao_addr_api_url}?page=1&AddressSize=1&query='{road_addr}'",
                                      headers=headers)
        if "documents" not in resp:
            print(f"err : not exist data {road_addr}")
            return {}

        if not resp["documents"]:
            return {}

        return resp["documents"][0]

    def _find_per_page_from_db(self, page_size, page_num):
        """
        페이지 단위로 데이터베이스에서 데이터 로드
        :param page_size: 한 페이지에 포함될 데이터 수
        :param page_num: 페이지 번호
        :return: 데이터베이스에서 가져온 데이터 리스트
        """
        skips = page_size * (page_num - 1)

        cursor = self.db.find().skip(skips).limit(page_size)

        return [x for x in cursor]


if __name__ == "__main__":
    o = ConvertCoordinate()
    # 몽고디비에서 페이징 처리해서 데이터 가져오기
    # r = o.find_per_page_from_db(page_size=1000, page_num=10)
    # 좌표 변환
    o.convert_wcongnamul_to_wgs84()
