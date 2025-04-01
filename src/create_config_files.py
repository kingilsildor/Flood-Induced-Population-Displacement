import re

import numpy as np
import pandas as pd

from src.config_file import PATH
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


def create_flood_level_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a flood level CSV file for the given data.
    Note: The DataFrame should contain the following columns:
    - Date: The date of the flood level.
    - Water Level Classification: The water level classification of the flood.
    This can be done by running the append_coords function.

    Params
    ------
    - df (pd.DataFrame): The DataFrame containing the flood level data.

    Returns
    -------
    - flood_level_df (pd.DataFrame): The DataFrame with the flood level data.
    """
    locations_df = get_locations()
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


def create_floodawareness_csv(flood_awareness: np.ndarray) -> pd.DataFrame:
    """
    Create a flood awareness CSV file for the given data.

    Params
    ------
    - flood_awareness (np.ndarray): The flood awareness data.

    Returns
    -------
    - flood_awareness_df (pd.DataFrame): The DataFrame with the flood awareness data.
    """
    assert isinstance(flood_awareness, np.ndarray), (
        "flood_awareness must be a numpy array"
    )

    locations_df = get_locations()
    locations_list = locations_df["#name"].tolist()

    flood_awareness_df = pd.DataFrame(columns=["floodawareness"] + locations_list)
    for col in flood_awareness_df.columns:
        flood_awareness_df.loc[:, col] = flood_awareness

    flood_awareness_df.to_csv(
        f"{PATH}input_csv/demographics_floodawareness.csv", index=False
    )
    return flood_awareness_df


def create_source_data_files(displacement_to_camps: int = 5000) -> None:
    """
    Create source data files for the given displacement to camps.
    
    Params
    ------
    - displacement_to_camps (int): The number of people displaced to camps. Default is 5000.
    """
    locations_df = get_locations()
    locations_list = locations_df["#name"].tolist()

    camp_locations = [location for location in locations_list if "camp" in location.lower()]
    diplacement_camp = int(displacement_to_camps / len(camp_locations))

    for location in locations_list:
        template_df = pd.DataFrame(columns=[["#Day", "Displacement"]], data=[
            ["2024-09-08",0],
            ["2024-09-14",0],
            ["2024-09-30",0] 
        ])

        if "camp" in location.lower():
            template_df["Displacement"] = [diplacement_camp] * len(template_df)
        else:
            template_df["Displacement"] = [0] * len(template_df) 

        template_df.to_csv(f"{PATH}source_data/{location}.csv", index=False, header=False)

def create_data_layout() -> None:
    """
    Create a data layout CSV file to define the csv files
    """
    locations_df = get_locations()
    locations_df.to_csv(f"{PATH}input_csv/location.csv", index=False)

    data_layout_df = pd.DataFrame(columns=["total", "refugees.csv"])
    data_layout_df["total"] = locations_df["#name"].tolist()
    data_layout_df["refugees.csv"] = [location + ".csv" for location in locations_df["#name"].tolist()]

    data_layout_df.to_csv(f"{PATH}source_data/data_layout.csv", index=False)