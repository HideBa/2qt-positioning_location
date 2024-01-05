import json
import math
import re
import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point, Polygon, mapping


def transform_point(point, source_crs, target_crs):
    transformer = Transformer.from_crs(
        f"epsg:{source_crs}", f"epsg:{target_crs}", always_xy=True
    )

    # Transform each point in the polygon
    transformed_point = transformer.transform(point.x, point.y)

    # Create a new polygon with the transformed points
    transformed_point = Point(transformed_point)

    return transformed_point


def transform_polygon(polygon, source_crs, target_crs):
    transformer = Transformer.from_crs(
        f"epsg:{source_crs}", f"epsg:{target_crs}", always_xy=True
    )

    # Transform each point in the polygon
    transformed_points = [
        transformer.transform(x, y) for x, y in polygon.exterior.coords
    ]

    # Create a new polygon with the transformed points
    transformed_polygon = Polygon(transformed_points)

    return transformed_polygon


def dms_to_decimal(dms):
    # Parse the DMS string
    parts = re.split("[°'\"]+", dms)
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    direction = parts[3]

    # Convert to decimal degrees
    decimal = degrees + minutes / 60 + seconds / 3600

    # Adjust for direction
    if direction in ["S", "W"]:
        decimal = -decimal

    return decimal


def convert_cocircle_to_circle(polygon):
    exterior_points = [Point(x, y) for x, y in polygon.exterior.coords]
    exterior_points = cocircle_points_to_circle(exterior_points)
    circle_polygon = Polygon([[p.x, p.y] for p in exterior_points])

    return circle_polygon


def cocircle_points_to_circle(points):
    circle = circimcircle_center(points[0], points[1], points[2])
    radius = math.sqrt((points[0].x - circle[0]) ** 2 + (points[0].y - circle[1]) ** 2)
    N = 20
    step = 2.0 * math.pi / N
    pts = []
    for i in range(N):
        pts.append(
            Point(
                circle[0] + math.cos(i * step) * radius,
                circle[1] + math.sin(i * step) * radius,
            )
        )
    return pts


def circimcircle_center(p0, p1, p2):
    ax, ay = p0.x, p0.y
    bx, by = p1.x, p1.y
    cx, cy = p2.x, p2.y
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if d == 0:
        return None
    ux = (
        (ax**2 + ay**2) * (by - cy)
        + (bx**2 + by**2) * (cy - ay)
        + (cx**2 + cy**2) * (ay - by)
    ) / d
    uy = (
        (ax**2 + ay**2) * (cx - bx)
        + (bx**2 + by**2) * (ax - cx)
        + (cx**2 + cy**2) * (bx - ax)
    ) / d
    return [ux, uy]


def export_polygons_to_geojson(polygon, filepath):
    with open(filepath, "w") as f:
        geojson_dict = mapping(polygon)

        geojson_structure = {
            "type": "Feature",
            "properties": {},
            "geometry": geojson_dict,
        }
        f.write(json.dumps(geojson_structure))
