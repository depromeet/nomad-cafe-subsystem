import geo_util


class Cafe:
    def __init__(self,
                 data_id,
                 data_type,
                 name,
                 x,
                 y,
                 create_dt,
                 update_dt,
                 parcel_addr=None,
                 road_addr=None,
                 phone=None,
                 start_hours=None,
                 end_hours=None,
                 tags={}):
        self._id = f"{data_type}-{data_id}"
        self.data_id = data_id
        self.name = name
        self.parcel_addr = parcel_addr
        self.road_addr = road_addr
        self.start_hours = start_hours
        self.end_hours = end_hours
        self.phone = phone
        self.tags = tags
        self.create_dt = create_dt
        self.update_dt = update_dt

        (lon, lat) = geo_util.GeoUtil.transform_location(x, y)
        self.location = {
            "type": "Point",
            "coordinates": [
                lon, lat
            ]
        }

        self.valid()

    def __repr__(self):
        return f"name: {self.name}, addr: {self.road_addr}, addr old: {self.parcel_addr}, " \
            f"coordinates: {self.location['coordinates']}"

    def __str__(self):
        return f"{self.name}, {self.road_addr}, {self.parcel_addr}, {self.location['coordinates']}"

    def valid(self):
        if self._id == "":
            raise Exception("not exist id", self)
        if self.name == "":
            raise Exception("not exist name", self)
        if self.location is None:
            raise Exception("not exist location", self)


