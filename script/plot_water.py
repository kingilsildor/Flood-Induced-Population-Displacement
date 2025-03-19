import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator
from src.config_file import FIG_DPI, FIG_SIZE


def plot_water_level(df: pd.DataFrame, danger_level: int, x: int, title: str) -> None:
    """
    Plot the water level and its classification.
    Note: The DataFrame should contain the following columns:
    - Day: The date of the water level.
    - Water level at (12:30) hr (cm): The water level at 12:30 PM.
    - Water Level Classification: The classification of the water level.

    Params
    ------
    - df (pd.DataFrame): The DataFrame containing the water level data.
    - danger_level (int): The danger level of the water level.
    - x (int): The number of classes to classify the water level.
    - title (str): The title of the plot.

    """
    assert "Day" in df.columns, "The DataFrame should contain the 'Day' column."
    assert "Water level at (12:30) hr (cm)" in df.columns, (
        "The DataFrame should contain the 'Water level at (12:30) hr (cm)' column."
    )
    assert "Water Level Classification" in df.columns, (
        "The DataFrame should contain the 'Water Level Classification' column."
    )

    fig, ax1 = plt.subplots(figsize=(FIG_SIZE), dpi=FIG_DPI)

    # Water Level
    ax1.plot(
        df["Day"],
        df["Water level at (12:30) hr (cm)"],
        label="Water Level (cm)",
        color="b",
    )
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Water Level (cm)")
    ax1.tick_params(axis="y")
    ax1.grid(True, which="both", axis="x", linestyle="--", linewidth=0.5)

    # Danger Level
    plt.axhline(
        y=danger_level,
        color="black",
        linestyle="--",
        label=f"Danger Level ({danger_level} cm)",
    )

    # Classification
    ax2 = ax1.twinx()
    ax2.plot(
        df["Day"],
        df["Water Level Classification"],
        label="Water Level Classification",
        linestyle=":",
        color="r",
    )
    ax2.set_ylabel("Water Level Classification")
    ax2.tick_params(axis="y")
    ax2.set_ylim(-1, x + 1)
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

    fig.tight_layout()
    plt.title(title)
    fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9))
    plt.show()
