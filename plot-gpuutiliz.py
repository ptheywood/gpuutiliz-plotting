#! /usr/bin/env python3

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import pathlib
import argparse
import itertools

CONFIG_SNS_CONTEXT = "talk"
CONFIG_SNS_PALETTE = "Dark2"
CONFIG_SNS_STYLE = "darkgrid"
CONFIG_FIGSIZE_INCHES = (16, 20)
CONFIG_XLABEL = "time (s)"
CONFIG_XLIM = None # (0, None)
CONFIG_DPI = 96
SUBPLOTS = [
    {
        "title": "Temperature",
        "series": [
            {"col": "dev_temp_deg_c", "label": "Temp (c)"},
        ],
        "yim": (0, None)
    },
    {
        "title": "Power",
        "series": [
            {"col": "dev_power_w", "label": "Power (W)"},
        ],
        "yim": (0, None)
    },
    {
        "title": "Memory Usage",
        "series": [
            {"col": "dev_mem_used_mb", "label": "Memory Used (MB)"},
        ],
        "yim": (0, None)
    },
    {
        "title": "GPU Kernels",
        "series": [
            {"col": "dev_util_pc", "label": "GPU %"},
        ],
        "yim": (0, 101),
        "ylabel": "Utilisation (%)"
    },
    {
        "title": "Memory Utilisation",
        "series": [
            {"col": "dev_mem_used_pc", "label": "Memory Used %"},
            {"col": "dev_mem_io_pc", "label": "Memory IO %"},
        ],
        # "yim": (0, 101),
        "ylabel": "Utilisation (%)"
    },
]

def main():
    # cli
    parser = argparse.ArgumentParser(description="Plotting script for willfurnass/gpuutiliz data")
    parser.add_argument("-i", "--input-dev-filepath", type=pathlib.Path, required=True, help = "path to a gpuutiliz generated device log file")
    parser.add_argument("-o", "--output-filepath", type=pathlib.Path, required=False, help = "path for figure output", default="figure.png")
    parser.add_argument("--title", type=str, help="Figure super title")
    args = parser.parse_args()

    # load data
    df = pd.read_csv(args.input_dev_filepath, delim_whitespace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    # Convert the timestamp to a relative timestamp from the 0th value. 
    t0 = pd.to_datetime(df["timestamp"][0])
    df["timedelta"] = df["timestamp"] - t0
    df["timedelta"] = df["timedelta"].dt.total_seconds()

    # plot data
    sns.set_context(CONFIG_SNS_CONTEXT, rc={"lines.linewidth": 2.5})  
    sns.set_style(CONFIG_SNS_STYLE)
    
    subplot_count = len(SUBPLOTS)
    huecount = sum([len(sp["series"]) for sp in SUBPLOTS])
    palette = sns.color_palette(CONFIG_SNS_PALETTE, huecount)
    iterable_palette = itertools.cycle(palette)
    sns.set_palette(palette)
    fig, axes = plt.subplots(constrained_layout=True, nrows=subplot_count, sharex="col")
    fig.set_size_inches(CONFIG_FIGSIZE_INCHES[0], CONFIG_FIGSIZE_INCHES[1])
    # Plot each subplot
    for idx, subplot in enumerate(SUBPLOTS):
        ax = axes[idx]
        for series in subplot["series"]:
            colour = next(iterable_palette)
            sns.lineplot(
                data=df, 
                x="timedelta", 
                y=series["col"], 
                markers = False,
                dashes = True,
                ax=ax,
                color=colour,
                legend='brief',
                label=series["label"]
            )
            # Axis settings
            if CONFIG_XLABEL:
                ax.set(xlabel=CONFIG_XLABEL)
            if "label" in series and series["label"]:
                ax.set(ylabel=series["label"])

        # set the ylimit if specified
        if "ylim" in subplot and len(subplot["ylim"]) == 2:
            ax.set(ylim=subplot["ylim"])
        if CONFIG_XLIM is not None and len(CONFIG_XLIM) == 2:
            ax.set(xlim=CONFIG_XLIM)
        # configure the axis title
        if "title" in subplot and subplot["title"] is not None:
            ax.set(title=subplot["title"])
        if "ylabel" in subplot and subplot["ylabel"]:
            ax.set(ylabel=subplot["ylabel"])
        # move the legend via seaborn.
        sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    # Compute the figure super titletitle
    if args.title is not None:
        plt.suptitle(args.title)
    else:
        plt.suptitle(f"gpuutiliz: {args.input_dev_filepath}")
    # Save the image
    args.output_filepath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output_filepath, dpi=CONFIG_DPI, bbox_inches='tight')

if __name__ == "__main__":
    main()