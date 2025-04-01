import pandas as pd
from src.config_file import PATH


def get_locations() -> pd.DataFrame:
    """
    Get the location data from the CSV file.

    Returns
    -------
    - location_df (pd.DataFrame): The DataFrame containing the location data.
    """
    location_df = pd.read_csv(f"{PATH}input_csv/locations.csv")
    return location_df


def get_routes() -> pd.DataFrame:
    """
    Read the routes.csv file and return a pandas DataFrame

    Returns
    -------
    - pd.DataFrame: The edges DataFrame
    """
    routes_df = pd.read_csv(
        PATH + "input_csv/routes.csv",
        header=None,
        names=["location_1", "location_2", "distance (km)"],
    )
    return routes_df
