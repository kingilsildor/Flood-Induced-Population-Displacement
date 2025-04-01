import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from src.config_file import FIG_DPI, FIG_SIZE
from src.get_files import get_locations, get_routes


def create_locations_gdf(locations_df) -> tuple:
    """
    Create a GeoDataFrame from the locations DataFrame

    Params
    ------
    - locations_df (pd.DataFrame): The locations DataFrame

    Returns
    -------
    - location_gdf (gpd.GeoDataFrame): The locations GeoDataFrame
    - location_dict (dict): A dictionary mapping location names to their coordinates
    - location_type_colors (dict): A dictionary mapping location types to colors
    """
    locations_gdf = gpd.GeoDataFrame(
        locations_df,
        geometry=gpd.points_from_xy(locations_df.longitude, locations_df.latitude),
    )
    locations_gdf.set_crs(epsg=4326, inplace=True)
    location_dict = locations_gdf.set_index("#name")["geometry"].to_dict()
    locations_gdf = locations_gdf.to_crs(epsg=3857)

    location_type_colors = {
        "flood_zone": "blue",
        "town": "red",
        "camp": "green",
        "temple": "purple",
    }
    locations_gdf["color"] = locations_gdf["location_type"].map(location_type_colors)
    # Overrite the camp location to display them as temples
    locations_gdf.loc[
        locations_gdf["#name"].str.contains("temple", case=False, na=False), "color"
    ] = location_type_colors["temple"]

    return locations_gdf, location_dict, location_type_colors


def create_edges_gdf(location_dict, edges_df) -> gpd.GeoDataFrame:
    """
    Create a GeoDataFrame from the edges DataFrame

    Params
    ------
    - location_dict (dict): A dictionary mapping location names to their coordinates
    - edges_df (pd.DataFrame): The edges DataFrame

    Returns
    -------
    - edges_gdf (gpd.GeoDataFrame): The edges GeoDataFrame
    """
    lines = [
        LineString([location_dict[row["location_1"]], location_dict[row["location_2"]]])
        for _, row in edges_df.iterrows()
        if row["location_1"] in location_dict and row["location_2"] in location_dict
    ]
    edges_gdf = gpd.GeoDataFrame(geometry=lines)
    edges_gdf.set_crs(epsg=4326, inplace=True)
    edges_gdf = edges_gdf.to_crs(epsg=3857)

    return edges_gdf


def plot_route(edges_gdf, locations_gdf, location_type_colors) -> None:
    """
    Plot the fleeing routes around the given locations

    Params
    ------
    - edges_gdf (gpd.GeoDataFrame): The edges GeoDataFrame
    - locations_gdf (gpd.GeoDataFrame): The locations GeoDataFrame
    - location_type_colors (dict): A dictionary mapping location types to colors
    """
    location_counts = locations_gdf["color"].value_counts().to_dict()
    _, ax = plt.subplots(figsize=FIG_SIZE, dpi=FIG_DPI)

    edges_gdf.plot(ax=ax, color="black", linewidth=1, label="Edges")
    locations_gdf.plot(
        ax=ax, c=locations_gdf["color"], markersize=50, label="Locations"
    )

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    legend_elements = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=f"{loc_type} ({location_counts[color]})",
            markerfacecolor=color,
            markersize=10,
        )
        for loc_type, color in location_type_colors.items()
    ]
    ax.legend(handles=legend_elements, title="Location Type")

    plt.title("Fleeing Routes around the Sittaung River, Toungoo Township Myanmar")
    plt.tight_layout()
    plt.savefig("results/route_plot.png", dpi=300)
    plt.show()


def create_route_plot() -> None:
    """
    Create a plot of the fleeing routes around the given locations
    """
    locations_df = get_locations()
    edges_df = get_routes()
    locations_gdf, location_dict, location_type_colors = create_locations_gdf(
        locations_df
    )
    edges_gdf = create_edges_gdf(location_dict, edges_df)
    plot_route(edges_gdf, locations_gdf, location_type_colors)


if __name__ == "__main__":
    create_route_plot()
