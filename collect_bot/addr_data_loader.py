import json
from dataclasses import field, dataclass

import openpyxl
import shapefile

'''
용어 정리
- town : 동 (ex - 천호동)
- vilige : 도로명 (ex - 신정로)

기타
- 함수명에 지역명이 들어간 경우 해당 지역의 데이터만 조회
- 지역이 명시되지 않은 경우 전국 데이터 조회
'''


@dataclass
class AddrDataLoader:
    towns: list = field(default_factory=list)
    villiges: list = field(default_factory=list)

    # 출저 : https://financedata.github.io/posts/korea-area-code.html
    def load_seoul_towns_from_xlsx(self):
        # 엑셀파일 열기
        wb = openpyxl.load_workbook('national_division.xlsx')
        ws = wb.get_sheet_by_name("2013년")

        towns = []
        for r in ws.rows:
            if r[0].row < 3:  # 1 ~ 2번 라인은 헤더
                continue
            city_code = r[0].value  # 시도코드
            city_name = r[1].value  # 시도명칭
            district_code = r[2].value  # 시군구코드
            district_name = r[3].value  # 시군구명칭
            town_code = r[4].value  # 읍면동코드
            town_name = r[5].value  # 읍면동명칭

            if city_name != "서울특별시":
                continue

            towns.append(town_name)
            print(city_code, city_name, district_code, district_name, town_code, town_name)

        wb.close()

        self.towns = towns
        return self.towns

    # 출저 : http://www.gisdeveloper.co.kr/?p=2332
    def load_seoul_villages_from_shp(self):
        r = shapefile.Reader("LI.shp", encoding="cp949")
        self.villiges = r.records()
        return self.villiges

    # 출저 : https://financedata.github.io/posts/korea-area-code.html
    def load_towns_from_json(self):
        towns = []
        with open('national_division.json') as json_file:
            obj = json.load(json_file)
            if not obj:
                raise Exception("not exist seoul division data")

            if not obj["features"]:
                raise Exception("not exist seoul division features")

            for feature in obj["features"]:
                if not feature["properties"]:
                    continue
                if not feature["properties"]["name"]:
                    continue
                towns.append(feature['properties']['name'])

        self.towns = towns
        return self.towns

    # 출저 : https://www.juso.go.kr/addrlink/devAddrLinkRequestGuide.do?menu=roadApi
    def load_villiges_from_addr_api(self):
        with open('juso.json', encoding="utf-8") as json_file:
            self.villiges = json.load(json_file)
            if not self.villiges:
                raise Exception("not exist data")

            return self.villiges

        raise Exception("json file load fail")

    # 출저 : https://www.juso.go.kr/addrlink/devAddrLinkRequestGuide.do?menu=roadApi
    def load_towns_from_addr_api(self):
        if self.villiges:
            villiges = self.villiges
        else:
            villiges = self.load_villiges_from_addr_api()

        towns = []
        for feature in villiges:
            for key in feature.keys():
                towns.append(key)

        self.towns = towns
        return self.towns


if __name__ == "__main__":
    loader = AddrDataLoader()
    print(loader.load_towns_from_addr_api())
