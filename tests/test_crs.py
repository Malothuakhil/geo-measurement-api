import geopandas as gpd
from shapely.geometry import Point

from app.services.crs_service import choose_projected_crs


def test_utm_selection_for_wgs84():
    gdf = gpd.GeoDataFrame(
        {"name": ["test"]},
        geometry=[Point(78.4867, 17.3850)],
        crs="EPSG:4326",
    )
    crs = choose_projected_crs(gdf)
    assert crs.is_projected
    assert crs.to_epsg() == 32644
