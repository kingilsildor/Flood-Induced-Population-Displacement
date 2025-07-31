import os
import re
import shutil

import numpy as np
import pandas as pd
from src.get_files import get_locations


def extract_coords(point_str: str) -> tuple:
    """
    Extracts the latitude and longitude from the WKT point string.

    Params
    ------
    - point_str (str): The WKT point string.

    Returns
    -------
    - coords (tuple): The latitude and longitude coordinates
    """
    coords = re.findall(r"[-+]?\d*\.\d+|\d+", point_str)
    return float(coords[0]), float(coords[1])


def append_coords(df) -> pd.DataFrame:
    """
    Extracts the latitude and longitude from the WKT column and appends them to the dataframe.
    Note: The DataFrame should contain the following column:
    - WKT: The well-known text (WKT) representation of the geometry.

    Params
    ------
    - df (pd.DataFrame): The DataFrame containing the WKT column.

    Returns
    -------
    - df (pd.DataFrame): The DataFrame with the latitude and longitude columns appended.
    """
    df[["longitude", "latitude"]] = df["WKT"].apply(
        lambda x: pd.Series(extract_coords(x))
    )
    df.drop(columns=["WKT"], inplace=True)
    return df


def create_location_file(
    location_df: pd.DataFrame, region: str = "Toungoo", country: str = "Myanmar"
) -> None:
    """
    Create a location file for the given location data.
    Note: The DataFrame should contain the following columns:
    - name: The name of the location.
    - latitude: The latitude of the location.
    - longitude: The longitude of the location.
    This can be done by running the append_coords function.

    Params
    ------
    - location_df (pd.DataFrame): The DataFrame containing the location data.
    - region (str): The region of the location. Default is "Toungoo".
    - country (str): The country of the location. Default is "Myanmar".
    """
    df = pd.DataFrame(
        columns=[
            "#name",
            "region",
            "country",
            "latitude",
            "longitude",
            "location_type",
            "conflict_period",
            "population",
        ]
    )

    df = df.assign(
        **{
            "#name": location_df["name"],
            "region": region,
            "country": country,
            "latitude": location_df["latitude"],
            "longitude": location_df["longitude"],
        }
    )

    df["location_type"] = df["#name"].str.lower().str.replace(r"_\d+$", "", regex=True)
    df.sort_values(by="#name", inplace=True)
    return df


def create_flood_level_csv(df: pd.DataFrame, PATH: str) -> pd.DataFrame:
    """
    Create a flood level CSV file for the given data.
    Note: The DataFrame should contain the following columns:
    - Date: The date of the flood level.
    - Water Level Classification: The water level classification of the flood.
    This can be done by running the append_coords function.

    Params
    ------
    - df (pd.DataFrame): The DataFrame containing the flood level data.
    - PATH (str): The path to save the flood level CSV file.

    Returns
    -------
    - flood_level_df (pd.DataFrame): The DataFrame with the flood level data.
    """
    locations_df = get_locations(PATH)
    locations_list = locations_df["#name"].tolist()

    assert "Date" in df.columns, "Date column is missing in the DataFrame"
    assert "Water Level Classification" in df.columns, (
        "Water Level Classification column is missing in the DataFrame"
    )

    days = df["Date"].tolist()
    day_list = np.arange(len(days))
    flood_level = df["Water Level Classification"].tolist()
    flood_level_df = pd.DataFrame(columns=["#Day"] + locations_list)

    flood_level_df["#Day"] = day_list

    for i in range(len(locations_list)):
        location = locations_list[i].lower()

        if "temple" in location:
            adjusted_level = [0] * len(day_list)
        elif "camp" in location:
            adjusted_level = [max(0, level - 2) for level in flood_level]
        elif "town" in location:
            adjusted_level = [max(0, level - 1) for level in flood_level]
        else:
            adjusted_level = flood_level

        flood_level_df[locations_list[i]] = adjusted_level
    flood_level_df.to_csv(f"{PATH}input_csv/flood_level.csv", index=False)
    return flood_level_df


def create_floodawareness_csv(flood_awareness: np.ndarray, PATH: str) -> pd.DataFrame:
    """
    Create a flood awareness CSV file for the given data.

    Params
    ------
    - flood_awareness (np.ndarray): The flood awareness data.
    - PATH (str): The path to save the flood awareness CSV file.

    Returns
    -------
    - flood_awareness_df (pd.DataFrame): The DataFrame with the flood awareness data.
    """
    assert isinstance(flood_awareness, np.ndarray), (
        "flood_awareness must be a numpy array"
    )

    locations_df = get_locations(PATH)
    locations_list = locations_df["#name"].tolist()

    flood_awareness_df = pd.DataFrame(columns=["floodawareness"] + locations_list)
    for col in flood_awareness_df.columns:
        flood_awareness_df.loc[:, col] = flood_awareness

    flood_awareness_df.to_csv(
        f"{PATH}input_csv/demographics_floodawareness.csv", index=False
    )
    return flood_awareness_df


def create_source_data_files(
    PATH: str,
    population: int = 15567,
    displacement: int = 5000,
    fraction_displaced_camp: float = 0.93,
    fraction_stays_in_camp: float = 1.0,
    flood_displacement: bool = False,
    day: int = 14,
) -> None:
    """
    Create source data files for the given displacement to camps.

    Params
    ------
    - PATH (str): The path to save the source data files.
    - population (int): The total population in the area. Default is 15567.
    - displacement (int): The number of people displaced to camps. Default is 5000.
    - fraction_stays_in_camp (float): The fraction of people who stay in the camps. Default is 1.0 (Everyone stays).
    - flood_displacement (bool): Whether to include flood displacement data. Default is False.
    - day (int): The day of the simulation. Default is 14.
    """
    locations_df = get_locations(PATH)
    locations_list = locations_df["#name"].tolist()

    (
        camp_locations,
        temple_locations,
        floodzone_locations,
        displacement_camp,
        displacement_temple,
        floodzone_population,
    ) = _create_camp_and_floodzone_locations(
        locations_list,
        displacement,
        fraction_displaced_camp,
        population,
    )
    _create_source_data_files_for_locations(
        camp_locations,
        displacement_camp,
        displacement_temple,
        floodzone_population,
        fraction_stays_in_camp,
        flood_displacement,
        PATH,
    )
    _create_refugee_csv(PATH, day, displacement)


def _create_camp_and_floodzone_locations(
    locations_list: list,
    displacement: int,
    fraction_displaced_camp: float,
    population: int,
) -> None:
    """
    Create lists of camp and flood zone locations from the given locations list.

    Params
    ------
    - locations_list (list): The list of locations to process.
    - displacement (int): The number of people displaced to camps.
    - fraction_displaced_camp (float): The fraction of people displaced to camps.
    - population (int): The total population in the area.
    """
    camp_locations = []
    temple_locations = []
    floodzone_locations = []

    for location in locations_list:
        lower_location = location.lower()

        if "camp" in lower_location:
            camp_locations.append(location)

        if "temple" in lower_location:
            temple_locations.append(location)

        if "flood_zone" in lower_location:
            floodzone_locations.append(location)

    displacement_camp = int(
        (displacement * fraction_displaced_camp) / len(camp_locations)
    )
    displacement_temple = int(
        (displacement * (1 - fraction_displaced_camp)) / len(temple_locations)
    )
    floodzone_population = int(population / len(floodzone_locations))
    print(
        f"Displacement to camps: {displacement_camp}, Floodzone population: {floodzone_population}"
    )

    return (
        camp_locations,
        temple_locations,
        floodzone_locations,
        displacement_camp,
        displacement_temple,
        floodzone_population,
    )


def _create_source_data_files_for_locations(
    locations_list: list,
    displacement_camp: int,
    displacement_temple: int,
    floodzone_population: int,
    fraction_stays_in_camp: float,
    flood_displacement: bool,
    PATH: str,
) -> None:
    """
    Create source data files for the given locations.

    Params
    ------
    - locations_list (list): The list of locations to create source data files for.
    - displacement_camp (int): The number of people displaced to camps.
    - displacement_temple (int): The number of people displaced to temples.
    - floodzone_population (int): The population in the flood zone.
    - fraction_stays_in_camp (float): The fraction of people who stay in the camps.
    - flood_displacement (bool): Whether to include flood displacement data.
    - PATH (str): The path to save the source data files.
    """
    for location in locations_list:
        template_df = pd.DataFrame(
            columns=[["#Day", "Displacement"]],
            data=[["2024-09-08", 0], ["2024-09-14", 0], ["2024-09-30", 0]],
        )

        if "camp" in location.lower():
            template_df.loc[1, "Displacement"] = displacement_camp
            template_df.loc[2, "Displacement"] = int(
                displacement_camp * fraction_stays_in_camp
            )

        if "temple" in location.lower():
            template_df.loc[1, "Displacement"] = displacement_temple
            template_df.loc[2, "Displacement"] = int(
                displacement_temple * fraction_stays_in_camp
            )

        if "flood_zone" in location.lower() and flood_displacement:
            template_df.loc[0, "Displacement"] = floodzone_population
            template_df.loc[1, "Displacement"] = int(floodzone_population * 0.4)
            template_df.loc[2, "Displacement"] = int(floodzone_population * 0.1)

        template_df.to_csv(
            f"{PATH}source_data/{location}.csv", index=False, header=False
        )


def _create_refugee_csv(
    PATH: str,
    day: int = 14,
    refugee_numbers: int = 5000,
) -> None:
    """
    Create a refugee CSV file for the given day and number of refugees.

    Params
    ------
    - PATH (str): The path to save the refugee CSV file.
    - day (int): The day of the refugee data. Default is 14.
    - refugee_numbers (int): The number of refugees. Default is 5000.
    """
    refugee_df = pd.DataFrame(
        columns=["Date", "Refugee_numbers"],
        data=[[f"2024-09-{day:02d}", refugee_numbers]],
    )
    refugee_df.to_csv(f"{PATH}source_data/refugees.csv", index=False, header=True)


def create_data_layout(PATH: str) -> None:
    """
    Create a data layout CSV file to define the csv files

    Params
    ------
    - PATH (str): The path to save the data layout CSV file.
    """
    locations_df = get_locations(PATH)

    data_layout_df = pd.DataFrame(columns=["total", "refugees.csv"])
    data_layout_df["total"] = locations_df["#name"].tolist()
    data_layout_df["refugees.csv"] = [
        location + ".csv" for location in locations_df["#name"].tolist()
    ]

    data_layout_df.to_csv(f"{PATH}source_data/data_layout.csv", index=False)


def copy_settings(PATH: str) -> None:
    """
    Copy the directory

    Params
    ------
    - PATH (str): The path to the directory to copy.
    """
    PATH_list = PATH.split("/")

    config_dir = PATH_list[-2]
    base_path = "/".join(PATH_list[:-2]) + "/"
    original_path = "/".join(PATH_list[:-1]) + "/"
    copy_path = os.path.join(base_path + config_dir + "_copy")

    i = 1
    while os.path.exists(f"{copy_path}{i}/"):
        i += 1

    copy_path = f"{copy_path}{i}/"
    shutil.copytree(original_path, copy_path)
