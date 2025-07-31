import contextily as ctx
import geopandas as gpd
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
from shapely.geometry import LineString
from src.get_files import get_locations, get_routes

plt.style.use("bmh")


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


def plot_route(
    edges_gdf: gpd.GeoDataFrame,
    locations_gdf: gpd.GeoDataFrame,
    location_type_colors: dict,
    FIG_DPI: int,
    FIG_SIZE: tuple,
) -> None:
    """
    Plot the fleeing routes around the given locations

    Params
    ------
    - edges_gdf (gpd.GeoDataFrame): The edges GeoDataFrame
    - locations_gdf (gpd.GeoDataFrame): The locations GeoDataFrame
    - location_type_colors (dict): A dictionary mapping location types to colors
    - FIG_DPI (int): The DPI for the figure
    - FIG_SIZE (tuple): The size of the figure
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

    plt.title("Fleeing Routes around the Sittaung River, Taungoo Township Myanmar")
    plt.tight_layout()
    plt.savefig("plots/route_plot.png", dpi=300)
    plt.show()


def plot_map(
    locations_gdf: gpd.GeoDataFrame,
    location_type_colors: dict,
    FIG_DPI: int,
    FIG_SIZE: tuple,
) -> None:
    """
    Plot the locations on a map with their respective colors

    Params
    ------
    - locations_gdf (gpd.GeoDataFrame): The locations GeoDataFrame
    - location_type_colors (dict): A dictionary mapping location types to colors
    - FIG_DPI (int): The DPI for the figure
    - FIG_SIZE (tuple): The size of the figure
    """
    location_counts = locations_gdf["color"].value_counts().to_dict()
    _, ax = plt.subplots(figsize=FIG_SIZE, dpi=FIG_DPI)
    locations_gdf.plot(ax=ax, c=locations_gdf["color"], markersize=50)

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    text_nudge = 10
    for idx, row in locations_gdf.iterrows():
        text = ax.text(
            row.geometry.x,
            row.geometry.y + text_nudge
            if idx % 2 == 0
            else row.geometry.y - text_nudge,
            row["#name"],
            fontsize=8,
            ha="center",
            va="center",
            color="white",
            weight="bold",
            zorder=5,
        )

        text.set_path_effects(
            [
                path_effects.Stroke(linewidth=1.5, foreground="black"),
                path_effects.Normal(),
            ]
        )

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

    plt.title("Locations around the Sittaung River, Taungoo Township Myanmar")
    plt.tight_layout()
    plt.savefig("plots/locations_map.png", dpi=300)
    plt.show()


def add_scale_bar(ax: matplotlib.axes.Axes, length_km: float, location: str) -> None:
    """
    Add a scale bar to the plot

    Params
    ------
    - ax (matplotlib.axes.Axes): The axis to add the scale bar to
    - length_km (float): The length of the scale bar in kilometers
    - location (str): The location of the scale bar on the plot, either "lower right" or "lower left"
    """
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Convert kilometers to degrees
    # Assuming 1 degree latitude is approximately 111 km
    deg_per_km = 1 / 111.0
    length_deg = length_km * deg_per_km

    if location == "lower right":
        x_start = xlim[1] - (xlim[1] - xlim[0]) * 0.3
        y_pos = ylim[0] + (ylim[1] - ylim[0]) * 0.1
    elif location == "lower left":
        x_start = xlim[0] + (xlim[1] - xlim[0]) * 0.05
        y_pos = ylim[0] + (ylim[1] - ylim[0]) * 0.1

    ax.plot([x_start, x_start + length_deg], [y_pos, y_pos], "k-", linewidth=3)
    ax.plot(
        [x_start, x_start],
        [y_pos - length_deg * 0.1, y_pos + length_deg * 0.1],
        "k-",
        linewidth=2,
    )
    ax.plot(
        [x_start + length_deg, x_start + length_deg],
        [y_pos - length_deg * 0.1, y_pos + length_deg * 0.1],
        "k-",
        linewidth=2,
    )

    ax.text(
        x_start + length_deg / 2,
        y_pos - length_deg * 0.3,
        f"{length_km} km",
        ha="center",
        va="top",
        fontsize=10,
        weight="bold",
    )


def plot_context_map() -> None:
    """
    Plot the context map of Myanmar with Taungoo Township highlighted
    """
    LAT, LON = 18.9436415, 96.4302635
    TAUNGOO_ROW = 54
    MYANMAR_REGION_BOUNDS = [88, 6, 102, 30]

    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(
        "Myanmar Regional Context and Taungoo Township Detail",
        fontsize=24,
    )

    ax1 = plt.subplot(121)
    ax2 = plt.subplot(122)

    world_countries = gpd.read_file(
        "input_data/geoshapes/world-administrative-boundaries.geojson"
    )
    myanmar_lvl3 = gpd.read_file(
        "input_data/geoshapes/mmr_polbnda_adm3_250k_mimu_1.shp"
    )

    taungoo_area = myanmar_lvl3.loc[TAUNGOO_ROW:TAUNGOO_ROW]

    bounds = taungoo_area.total_bounds
    buffer_x = 0.05
    buffer_y = 0.25
    minx, miny, maxx, maxy = bounds

    buffered_bounds = [
        minx - buffer_x,
        miny - buffer_y,
        maxx + buffer_x,
        maxy + buffer_y,
    ]

    regional_countries = world_countries.cx[
        MYANMAR_REGION_BOUNDS[0] : MYANMAR_REGION_BOUNDS[2],
        MYANMAR_REGION_BOUNDS[1] : MYANMAR_REGION_BOUNDS[3],
    ]

    regional_countries.plot(ax=ax1, color="lightgray", edgecolor="black", linewidth=0.5)
    country_columns = ["name", "NAME", "country", "COUNTRY", "NAME_EN", "admin"]
    myanmar_country = None

    for col in country_columns:
        if col in regional_countries.columns:
            myanmar_country = regional_countries[
                regional_countries[col].str.contains(
                    "Myanmar|Burma", case=False, na=False
                )
            ]
            if not myanmar_country.empty:
                break

    if myanmar_country is not None and not myanmar_country.empty:
        myanmar_country.plot(
            ax=ax1, color="lightblue", edgecolor="black", linewidth=1.0
        )

    _axis1_plot(ax1, LON, LAT, MYANMAR_REGION_BOUNDS)
    _axis2_plot(ax2, taungoo_area, buffered_bounds, LON, LAT)

    plt.tight_layout()
    plt.savefig("plots/context_map.png", dpi=300)
    plt.show()


def _axis1_plot(
    ax1: matplotlib.axes.Axes, LON: float, LAT: float, MYANMAR_REGION_BOUNDS: list
) -> None:
    """
    Plot the main map of Myanmar with Taungoo Township highlighted.

    Params
    ------
    - ax1 (matplotlib.axes.Axes): The axis to plot on
    - LON (float): Longitude of Taungoo
    - LAT (float): Latitude of Taungoo
    - MYANMAR_REGION_BOUNDS (list): The bounds of the Myanmar region
    """
    ax1.plot(LON, LAT, "ro", markersize=8, label=f"Taungoo ({LAT}, {LON})")
    ax1.text(
        LON + 0.5,
        LAT + 0.5,
        "Taungoo",
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )
    ax1.axis("off")

    ax1.set_xlim(MYANMAR_REGION_BOUNDS[0], MYANMAR_REGION_BOUNDS[2])
    ax1.set_ylim(MYANMAR_REGION_BOUNDS[1], MYANMAR_REGION_BOUNDS[3])
    add_scale_bar(ax1, 200, "lower left")


def _axis2_plot(
    ax2: matplotlib.axes.Axes,
    taungoo_area: gpd.GeoDataFrame,
    buffered_bounds: list,
    LON: float,
    LAT: float,
) -> None:
    """
    Plot the context map for Taungoo Township.

    Params
    ------
    - ax2 (matplotlib.axes.Axes): The axis to plot on
    - taungoo_area (gpd.GeoDataFrame): The GeoDataFrame containing Taungoo area geometry
    - buffered_bounds (list): The buffered bounds for the plot
    - LON (float): Longitude of Taungoo
    - LAT (float): Latitude of Taungoo
    """

    ax2.set_xlim(buffered_bounds[0], buffered_bounds[2])
    ax2.set_ylim(buffered_bounds[1], buffered_bounds[3])

    try:
        ctx.add_basemap(
            ax=ax2,
            crs="EPSG:4326",
            source=ctx.providers.OpenStreetMap.Mapnik,
            alpha=0.8,
        )
    except Exception as e:
        print(f"Could not add basemap: {e}")

    taungoo_area.plot(
        ax=ax2,
        facecolor="none",
        edgecolor="black",
        linewidth=2.0,
        alpha=0.8,
    )

    ax2.plot(LON, LAT, "ro", markersize=10, label=f"Taungoo ({LAT}, {LON})")
    ax2.text(
        LON + 0.01,
        LAT + 0.01,
        "Taungoo",
        fontsize=12,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9),
    )

    ax2.set_xlim(buffered_bounds[0], buffered_bounds[2])
    ax2.set_ylim(buffered_bounds[1], buffered_bounds[3])
    add_scale_bar(ax2, 10, "lower right")


def create_route_plot(FIG_DPI: int, FIG_SIZE: tuple, PATH: str) -> None:
    """
    Create a plot of the fleeing routes around the given locations

    Params
    ------
    - FIG_DPI (int): The DPI for the figure
    - FIG_SIZE (tuple): The size of the figure
    - PATH (str): The path to the input data files
    """
    locations_df = get_locations(PATH)
    edges_df = get_routes(PATH)
    locations_gdf, location_dict, location_type_colors = create_locations_gdf(
        locations_df
    )
    edges_gdf = create_edges_gdf(location_dict, edges_df)
    plot_route(edges_gdf, locations_gdf, location_type_colors, FIG_DPI, FIG_SIZE)
    plot_map(locations_gdf, location_type_colors, FIG_DPI, FIG_SIZE)


if __name__ == "__main__":
    create_route_plot(FIG_DPI=300, FIG_SIZE=(8, 6))
