from dataclasses import dataclass, field
import datetime
import geo_util


@dataclass
class Cafe:
    data_id: str
    data_type: str
    name: str
    x: str
    y: str
    _id: str = ""
    region_1depth_name: str = ""
    region_2depth_name: str = ""
    region_3depth_name: str = ""
    road_name: str = ""
    parcel_addr: str = ""
    road_addr: str = ""
    phone: str = ""
    zipcode: str = ""
    homepage: str = ""
    brand_name: str = ""
    img: str = ""
    tags: dict = field(default_factory=dict)
    location: dict = field(default_factory=dict)
    create_dt: datetime.date = datetime.datetime.utcnow()
    update_dt: datetime.date = datetime.datetime.utcnow()

    def __post_init__(self):
        self._id = f"{self.data_type}-{self.data_id}"
        (lon, lat) = geo_util.GeoUtil.transform_location(self.x, self.y)
        self.location = {
            "type": "Point",
            "coordinates": [
                lon, lat
            ]
        }

        self.valid()

    def valid(self):
        if not self._id:
            raise Exception("not exist id", self)
        if not self.name:
            raise Exception("not exist name", self)
        if not self.location:
            raise Exception("not exist location", self)


if __name__ == "__main__":
    print(Cafe(data_id="id-1234", data_type="sample", name="sample", x="196078.0075", y="442261.8928"))
