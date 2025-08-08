import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def _create_file_path(
    file_name: str, normalize: bool, show_values: bool, subtitle: str, results_dir: str
):
    """
    Create a file path for saving plots based on the provided parameters.

    Params:
    ---------
    - file_name (str): Base name for the file.
    - normalize (bool): Whether the plot is normalized.
    - show_values (bool): Whether to show values in the plot.
    - subtitle (str): Subtitle for the plot, used in the filename.
    - results_dir (str): Directory where the plot will be saved.

    Returns:
    ---------
    - path (str): Full path to the file where the plot will be saved.
    """
    filename_parts = [file_name]

    if normalize:
        filename_parts.append("normalized")
    if show_values:
        filename_parts.append("show_values")

    clean_subtitle = subtitle.replace(" ", "_").lower()
    filename_parts.append(clean_subtitle)

    filename = "_".join(filename_parts) + ".png"
    path = f"{results_dir}/{filename}"
    return path


def error_matrix(
    df,
    daytick_labels,
    subtitle="",
    normalize=False,
    show_values=False,
    show_plot=False,
    results_dir="plots",
) -> None:
    """
    Create a heatmap of errors from the DataFrame.

    Params:
    ---------
    - df (pd.DataFrame): DataFrame containing error data with a "Date" column.
    - daytick_labels (list): Labels for the x-axis ticks.
    - subtitle (str): Subtitle for the plot. Default is an empty string.
    - normalize (bool): Whether to normalize the error values. Default is False.
    - show_values (bool): Whether to display values in the heatmap cells. Default is False.
    - show_plot (bool): Whether to display the plot immediately. Default is False.
    - results_dir (str): Directory to save the heatmap PNG file. Default is "plots".

    Returns:
    ---------
    - None: Displays the heatmap and saves it as a PNG file.
    """

    error_cols = [
        col
        for col in df.columns
        if "error" in col.lower()
        and "total" not in col.lower()
        and "std" not in col.lower()
    ]
    error_data = df[error_cols].copy()
    error_data.index = pd.to_datetime(df["Date"])
    error_data.columns = error_data.columns.str.replace(" error", "")

    error_data_T = error_data.T
    max_val = error_data_T.max().max()
    if normalize and max_val != 0:
        error_data_T = error_data_T / max_val

    plt.figure(figsize=(16, 8))
    heatmap = sns.heatmap(
        error_data_T,
        cmap="plasma",
        annot=show_values,
        fmt=".2f" if show_values else "",
        cbar_kws={
            "label": "Normalized Error Magnitude" if normalize else "Error Magnitude"
        },
        linewidths=0.01,
    )

    heatmap.set_xticks(np.arange(len(daytick_labels)) + 0.5)
    heatmap.set_xticklabels(daytick_labels, rotation=45)

    title = "Average Error Heatmap for Camps and Temples Over Time"
    if subtitle:
        title += f"\n{subtitle}"
    plt.title(title)

    plt.xlabel("Date")
    plt.ylabel("Location")
    plt.tight_layout()
    plt.grid(False)

    path = _create_file_path(
        "error_heatmap",
        normalize=normalize,
        show_values=show_values,
        subtitle=subtitle,
        results_dir=results_dir,
    )

    if show_plot:
        plt.show()
    else:
        plt.savefig(path, dpi=300)
        plt.close()


def displacement_over_time(
    days: list,
    refugee_series: list,
    refugee_std_series: list,
    daytick_labels: list,
    series_labels: list,
    normalize: bool = False,
    show_plot: bool = False,
    results_dir: str = "plots",
    name: str = None,
) -> None:
    """
    Plot the average number of displaced individuals over time.

    Params:
    ---------
    - days (list): List of days corresponding to the x-axis.
    - refugee_series (list of lists): List containing series of displaced individuals.
    - refugee_std_series (list of lists): List containing standard deviations for each series.
    - daytick_labels (list): Labels for the x-axis ticks.
    - series_labels (list): Labels for each series in the plot.
    - normalize (bool): Whether to normalize the data. Default is False.
    - show_plot (bool): Whether to display the plot immediately. Default is False.
    - results_dir (str): Directory to save the plot PNG file. Default is "plots".
    - name (str): Name for the plot file. If None, a default name will be generated.

    Returns:
    ---------
    - None: Displays the plot and saves it as a PNG file.
    """
    plt.figure(figsize=(10, 5))
    ax = plt.gca()

    plots = len(refugee_series)

    for series, std, label in zip(refugee_series, refugee_std_series, series_labels):
        data = np.array(series)

        max_val = data.max()
        if normalize and max_val != 0:
            data = data / max_val

        if std is not None:
            std = np.array(std)
            ax.fill_between(
                days,
                data - std,
                data + std,
                alpha=0.2,
            )
        ax.plot(days, data, label=label)

    ax.set_xticks(np.arange(len(daytick_labels)))
    ax.set_xticklabels(daytick_labels, rotation=45, ha="right")

    ax.set_xlabel("Date")
    ax.set_ylabel(
        "Average normalized Displaced Individuals"
        if normalize
        else "Average Displaced Individuals"
    )

    ax.legend()
    plt.tight_layout()

    if show_plot:
        plt.show()
    else:
        plt.savefig(
            f"{results_dir}/displacement_over_time_{plots}.png"
            if not name
            else f"{results_dir}/displacement_over_time_{name}.png",
            dpi=300,
        )
        plt.close()


def camp_displacement(
    days: list,
    dfs: list,
    df_labels: list,
    daytick_labels: list,
    N_camps: int = 8,
    is_camp: bool = True,
    show_plot: bool = False,
    results_dir: str = "plots",
) -> None:
    """
    Plot the average number of displaced individuals per camp over time.

    Params:
    ---------
    - days (list): List of days corresponding to the x-axis.
    - dfs (list of pd.DataFrame): List of DataFrames containing displacement data.
    - df_labels (list): Labels for each DataFrame in the plot.
    - daytick_labels (list): Labels for the x-axis ticks.
    - N_camps (int): Number of camps to consider. Default is 8.
    - is_camp (bool): Whether to plot per camp or not. Default is True.
    - show_plot (bool): Whether to display the plot immediately. Default is False.
    - results_dir (str): Directory to save the plot PNG file. Default is "plots".
    """
    nrows = 2
    ncols = math.ceil(N_camps / nrows)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(20, 10))
    axes = axes.flatten() if nrows * ncols > 1 else [axes]

    for i in range(N_camps):
        ax = axes[i]
        for df, label in zip(dfs, df_labels):
            if is_camp:
                camp_col = f"Camp_{i + 1} sim"
                std_col = f"Camp_{i + 1} sim (std)"
            else:
                camp_col = f"Temple_{i + 1} sim"
                std_col = f"Temple_{i + 1} sim (std)"

            data = df[camp_col].values
            std = df[std_col].values

            ax.fill_between(
                days,
                data - std,
                data + std,
                alpha=0.2,
            )
            ax.plot(days, data, label=label)

            ax.set_title(
                f"Camp {i + 1}" if is_camp else f"Temple {i + 1}",
                fontsize=15,
                fontweight="bold",
            )

            ax.legend(
                fontsize=10,
                loc="lower right",
                prop={"weight": "bold"},
            )

            ax.set_xticks(np.arange(len(daytick_labels)))
            ax.set_xticklabels(daytick_labels, fontsize=10, rotation=45, ha="right")

            ax.set_yscale("log")
            ax.set_ylim(10**-1, 3 * 10**3)  # Set y-axis limits for better visibility

    label_size = 25
    fig.supxlabel("Days", fontsize=label_size)
    fig.supylabel(
        "Average Amount of Displaced Individuals at a given location",
        fontsize=label_size - 5,
        x=0.01,  # Adjust x position for better visibility
    )

    plt.tight_layout()

    if show_plot:
        plt.show()
    else:
        plt.savefig(f"{results_dir}/camp_over_time_{is_camp}.png", dpi=500)
        plt.close()
