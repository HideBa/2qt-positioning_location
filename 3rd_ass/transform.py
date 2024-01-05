import json
import pandas as pd
from shapely.geometry import Point, Polygon

from common import (
    transform_point,
    transform_polygon,
    dms_to_decimal,
    export_polygons_to_geojson,
    convert_cocircle_to_circle,
)


def convert_csv_to_polygon(filepath):
    df = pd.read_csv(filepath, header=None)
    df.columns = ["id", "lat", "lng", "height"]
    # convert lat and lng from DMS to Decimal
    df["lat"] = df["lat"].apply(dms_to_decimal)
    df["lng"] = df["lng"].apply(dms_to_decimal)

    # # Create Points from DataFrame
    points = [Point(xy) for xy in zip(df["lng"], df["lat"])]

    # Create a Polygon
    polygon = Polygon([[p.x, p.y] for p in points])
    return polygon


def write_points(input, output):
    df = pd.read_csv(input, header=None)
    df.columns = ["id", "lat", "lng", "height"]
    # convert lat and lng from DMS to Decimal
    df["lat"] = df["lat"].apply(dms_to_decimal)
    df["lng"] = df["lng"].apply(dms_to_decimal)
    points = [Point(xy) for xy in zip(df["lng"], df["lat"])]
    reprojected_points = [transform_point(p, "9286", "4326") for p in points]
    properties = df["id"].to_list()
    properties = [{"id": p} for p in properties]
    features = []
    print("reprojected_points", reprojected_points[0])
    for point, prop in zip(reprojected_points, properties):
        feature = {
            "type": "Feature",
            "properties": prop,
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


def main():
    etrs89_lib_polygon = convert_csv_to_polygon("./3rd_ass/data/rtk_lib.csv")
    etrs89_cone_polygon = convert_cocircle_to_circle(
        convert_csv_to_polygon("./3rd_ass/data/rtk_cone.csv")
    )
    wgs84_lib_polygon = transform_polygon(etrs89_lib_polygon, "9286", "4326")
    wgs84_cone_polygon = transform_polygon(etrs89_cone_polygon, "9286", "4326")
    wgs84_lib_grass_polygon = Polygon(
        shell=wgs84_lib_polygon.exterior.coords,
        holes=[wgs84_cone_polygon.exterior.coords],
    )

    export_polygons_to_geojson(
        wgs84_lib_grass_polygon, "./3rd_ass/data/debug/rtk.geojson"
    )
    write_points(
        "./3rd_ass/data/rtk_lib.csv", "./3rd_ass/data/debug/lib_points.geojson"
    )
    write_points(
        "./3rd_ass/data/rtk_cone.csv", "./3rd_ass/data/debug/cone_points.geojson"
    )


if __name__ == "__main__":
    main()
