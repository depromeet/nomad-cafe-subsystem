import geo_converter


class GeoUtil:
    @staticmethod
    def transform_location(x, y):
        if not x or not y:
            raise Exception("x, y code are empty")

        x = float(x)
        y = float(y)
        pt = geo_converter.GeoPoint(x, y)
        output = geo_converter.convert(geo_converter.TM, geo_converter.GEO, pt)
        return output.getX(), output.getY()  # x=Longitude(경도), y=Latitude(위도)
