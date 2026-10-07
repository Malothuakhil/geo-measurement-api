import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

gdf = gpd.GeoDataFrame(
    {"name": ["Area A", "Road A", "Point A"],
     "geometry": [
         Polygon([(78.48,17.38),(78.49,17.38),(78.49,17.39),(78.48,17.39)]),
         LineString([(78.48,17.38),(78.49,17.39)]),
         Point(78.4867,17.3850),
     ]},
    crs="EPSG:4326"
)
gdf.to_file("sample.geojson", driver="GeoJSON")
print("Created sample.geojson")
