import pandas as pd


def get_locations(PATH: str) -> pd.DataFrame:
    """
    Get the location data from the CSV file.

    Params
    ------
    - PATH (str): The path to the CSV file containing location data.

    Returns
    -------
    - location_df (pd.DataFrame): The DataFrame containing the location data.
    """
    location_df = pd.read_csv(f"{PATH}input_csv/locations.csv")
    return location_df


def get_routes(PATH: str) -> pd.DataFrame:
    """
    Read the routes.csv file and return a pandas DataFrame

    Params
    ------
    - PATH (str): The path to the CSV file containing route data.

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
