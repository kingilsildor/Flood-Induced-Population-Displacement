import re

import pandas as pd


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
