import json
import re
from shapely.geometry import Polygon, Point
from common import export_polygons_to_geojson
import geopandas as gdp


def dms_to_decimal(degrees, minutes, direction):
    decimal = float(degrees) + float(minutes) / 60
    if direction in ["S", "W"]:
        decimal = -decimal
    return decimal


def extract_lat_lon(nmea_data):
    coords = []
    for line in nmea_data.splitlines():
        if line.startswith("$GPGGA"):
            # if line.startswith("$GPGGA") or line.startswith("$GPRMC"):
            parts = line.split(",")
            if len(parts) > 6 and parts[2] and parts[4]:
                lat = dms_to_decimal(parts[2][:2], parts[2][2:], parts[3])
                lon = dms_to_decimal(parts[4][:3], parts[4][3:], parts[5])
                coords.append((lon, lat))
    return coords


def create_polygon_from_coords(coords):
    if len(coords) >= 3:  # A polygon needs at least 3 points
        return Polygon(coords)
    else:
        return None


def write_points(points, output):
    points = [Point(xy) for xy in points]
    features = []
    for point in points:
        feature = {
            "type": "Feature",
            # "properties": prop,
            "geometry": {
                "type": "Point",
                "coordinates": [
                    point.x,
                    point.y,
                ],
            },
        }
        features.append(feature)
    geojson_structure = {"type": "FeatureCollection", "features": features}
    with open(output, "w") as f:
        f.write(json.dumps(geojson_structure))


def points_to_polygon(points):
    return Polygon([[p.x, p.y] for p in points])


def read_geojson(filepath):
    gdf = gdp.read_file(filepath)
    return gdf


def main():
    print("start")
    # Extract Points of grass
    # with open("./3rd_ass/data/nmea/lib.csv") as f:
    #     nmea_data = f.read()
    #     points = extract_lat_lon(nmea_data)
    #     polygon = create_polygon_from_coords(points)

    #     export_polygons_to_geojson(polygon, "./3rd_ass/data/debug/nmea_grass.geojson")
    #     write_points(points, "./3rd_ass/data/debug/nmea_points.geojson")

    # Extract points of cone
    # with open("./3rd_ass/data/nmea/cone.csv") as f:
    #     nmea_data = f.read()
    #     points = extract_lat_lon(nmea_data)
    #     polygon = create_polygon_from_coords(points)

    #     export_polygons_to_geojson(polygon, "./3rd_ass/data/debug/nmea_cone.geojson")
    #     write_points(points, "./3rd_ass/data/debug/nmea_cone_points.geojson")

    # Make polygon of grass
    # points = read_geojson("./3rd_ass/qgis/nmea_clean_points.geojson")
    # polygon = points_to_polygon(points.geometry)
    # export_polygons_to_geojson(polygon, "./3rd_ass/data/debug/nmea_polygon.geojson")

    # Make polygon of cone
    # points = read_geojson("./3rd_ass/data/debug/nmea_cone_points.geojson")
    # polygon = points_to_polygon(points.geometry)
    # export_polygons_to_geojson(
    #     polygon, "./3rd_ass/data/debug/nmea_cone_polygon.geojson"
    # )

    # # Create polygon with hole
    # grass_polygon = read_geojson("./3rd_ass/data/debug/nmea_polygon.geojson")
    # # print("grass:", grass_polygon.geometry.exterior.coords)
    # cone_polygon = read_geojson("./3rd_ass/data/debug/nmea_cone_polygon.geojson")
    # print("cone", cone_polygon)
    # polygon_with_hole = Polygon(
    #     shell=grass_polygon.geometry.iloc[0].exterior.coords,
    #     holes=[cone_polygon.geometry.iloc[0].exterior.coords],
    # )
    # export_polygons_to_geojson(polygon_with_hole, "./3rd_ass/data/debug/nmea.geojson")


if __name__ == "__main__":
    main()
