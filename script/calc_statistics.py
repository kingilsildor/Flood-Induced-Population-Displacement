import pandas as pd
import os


def get_statistics(
    file_name: str,
    N: int = 30,
    decimal_places: int = 2,
) -> pd.DataFrame:
    """
    Calculate per‑day mean and standard deviation of all numeric columns
    across multiple CSV files and save the combined results.

    Params
    ----------
    file_name : str
        Base name for the CSV files (e.g., "simulation_results/simulation_5000").
    N : int, default 30
        Number of files to aggregate.
    decimal_places : int, default 2
        Number of decimal places to round the output to.

    Returns
    -------
    pd.DataFrame
        DataFrame with non‑numeric identifier columns, mean values for every
        numeric column, and a std column for each numeric column named as
        "column_name (std)".
    """

    first_file = pd.read_csv(f"{file_name}_1.csv")

    numeric_cols = first_file.select_dtypes(include="number").columns
    non_numeric_cols = first_file.select_dtypes(exclude="number").columns

    sum_df = first_file[numeric_cols].copy()
    sq_sum_df = first_file[numeric_cols].pow(2)

    for i in range(2, N + 1):
        df = pd.read_csv(f"{file_name}_{i}.csv")
        sum_df += df[numeric_cols]
        sq_sum_df += df[numeric_cols].pow(2)

    mean_df = sum_df / N
    var_df = (sq_sum_df / N) - mean_df.pow(2)
    std_df = var_df.clip(lower=0).pow(0.5)

    mean_df = mean_df.round(decimal_places)
    std_df = std_df.round(decimal_places)

    std_df.columns = [f"{col} (std)" for col in std_df.columns]

    result_df = pd.concat(
        [first_file[non_numeric_cols].reset_index(drop=True), mean_df, std_df],
        axis=1,
    )

    assert isinstance(result_df, pd.DataFrame), "Result is not a DataFrame"

    result_df.to_csv(f"{file_name}.csv", index=False)
    return result_df


def get_sim_df(import_file: str = "simulation_results/") -> tuple:
    """
    Get the simulation DataFrame by aggregating results from multiple CSV files.

    Params
    ----------
    - import_file (str): Path to the directory containing simulation result files.

    Returns
    -------
    - df_5000 (pd.DataFrame): DataFrame with statistics for 5000 simulations.
    - df_12000 (pd.DataFrame): DataFrame with statistics for 12000 simulations.
    - df_lesshubs (pd.DataFrame): DataFrame with statistics for simulations with fewer hubs.
    - df_lessshelters (pd.DataFrame): DataFrame with statistics for simulations
    """
    files = os.listdir(import_file)
    print(f"Amount of simulation runs: {len(files)}")

    df_5000 = get_statistics(file_name=import_file + "5000")
    df_12000 = get_statistics(file_name=import_file + "12000")
    df_lesshubs = get_statistics(file_name=import_file + "lesshubs")
    df_lessshelters = get_statistics(file_name=import_file + "lessshelter")

    return df_5000, df_12000, df_lesshubs, df_lessshelters


def get_sim_dates(df: pd.DataFrame) -> tuple:
    """
    Get the dates for the simulation runs.

    Params
    ----------
    - df (pd.DataFrame): DataFrame containing a "Date" column with the simulation dates.

    Returns
    -------
    - days (list): List of dates from the "Date" column.
    - daytick_labels (list): List of formatted date labels for the x-axis ticks.
    """
    days = df["Date"]
    daytick_labels = [f"{i} Sep" for i in range(8, 31)]
    return days, daytick_labels
