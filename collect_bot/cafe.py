class Cafe:
    def __init__(self, name, parcel_addr, road_addr, start_hours, end_hours, phone, x, y, tags, create_dt, update_dt):
        self.name = name
        self.parcel_addr = parcel_addr
        self.road_addr = road_addr
        self.start_hours = start_hours
        self.end_hours = end_hours
        self.phone = phone
        self.x = x
        self.y = y
        self.tags = tags
        self.create_dt = create_dt
        self.update_dt = update_dt
        self.valid()

    def valid(self):
        if self.name == "":
            raise Exception("not exist name")
        if self.parcel_addr == "":
            raise Exception("not exist parcel_addr")
        if self.road_addr == "":
            raise Exception("not exist road_addr")
        if self.x == "":
            raise Exception("not exist x")
        if self.y == "":
            raise Exception("not exist y")
