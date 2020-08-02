import time

import cafe


class CafeFactory:
    def __init__(self):
        print()

    @staticmethod
    def new_cafe(data_type, data):
        return cafe.Cafe(
            data_id=int(data["ID"]),
            data_type=data_type,
            name=data["NM"],
            parcel_addr=data["ADDR_OLD"],
            road_addr=data["ADDR"],
            phone=data["TEL"],
            x=data["XCODE"],
            y=data["YCODE"],
            create_dt=time.time(),
            update_dt=time.time()
        )


