import math
import geopandas as gpd
from pyproj import CRS


def choose_projected_crs(gdf: gpd.GeoDataFrame) -> CRS:
    """Choose a local UTM CRS from the dataset centroid."""
    if gdf.crs is None:
        raise ValueError("Input file has no CRS. A CRS is required for measurement.")

    source = CRS.from_user_input(gdf.crs)
    if source.is_projected:
        return source

    centroid = gdf.to_crs("EPSG:4326").geometry.unary_union.centroid
    lon, lat = centroid.x, centroid.y
    zone = math.floor((lon + 180) / 6) + 1
    epsg = (32600 if lat >= 0 else 32700) + zone
    return CRS.from_epsg(epsg)
