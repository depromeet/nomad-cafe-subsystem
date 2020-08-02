import geo_converter


class GeoUtil:
    def __init__(self):
        print()

    @staticmethod
    def transform_location(x, y):
        pt = geo_converter.GeoPoint(x, y)
        output = geo_converter.convert(geo_converter.TM, geo_converter.GEO, pt)
        return output.getY(), output.getX()  # y=Latitude(위도), x=Longitude(경도)
