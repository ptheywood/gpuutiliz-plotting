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
    parser.add_argument("-o", "--output-filepath", nargs="+", type=pathlib.Path, required=False, help = "path for figure output", default="figure.png")
    parser.add_argument("--title", type=str, help="Figure super title")
    parser.add_argument("--rolling-mean", type=int, help="Plot a rolling average (mean) of N samples")
    args = parser.parse_args()

    # load data
    source_df = pd.read_csv(args.input_dev_filepath, delim_whitespace=True)
    source_df["timestamp"] = pd.to_datetime(source_df["timestamp"])
    # Convert the timestamp to a relative timestamp from the 0th value. 
    t0 = pd.to_datetime(source_df["timestamp"][0])
    source_df["timedelta"] = source_df["timestamp"] - t0
    source_df["timedelta"] = source_df["timedelta"].dt.total_seconds()

    # Create one dataframe per unique dev_uuid value in the source dataframe
    dfs = []
    for uuid in source_df["dev_uuid"].unique():
        dfs.append(source_df.query(f'dev_uuid == "{uuid}"'))

    # Error if the number of output files does not match the number of unique uuids

    if len(dfs) != len(args.output_filepath):
        raise Exception(f"Eroor: input file contained data for {len(dfs)} GPUs, but only {len(args.output_filepath)} values provided for -o,--output-filepath.")

    for df_idx, df in enumerate(dfs):
        # if a rolling mean is requested, compute the data as appropriate
        if args.rolling_mean is not None and args.rolling_mean > 1:
            cols = list(set([series["col"] for subplot in SUBPLOTS for series in subplot["series"]]))
            for col in cols:
                df[f"rolling_{col}"] = df[col].rolling(args.rolling_mean).mean().shift(int(-(args.rolling_mean / 2)))

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
                if args.rolling_mean:
                    colour = (*colour, 0.2)
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
                rolling_col = f"rolling_{series['col']}"
                if rolling_col in df.columns:
                    sns.lineplot(
                        data=df, 
                        x="timedelta", 
                        y="rolling_" + series["col"], 
                        markers = False,
                        dashes = True,
                        ax=ax,
                        color=colour[0:3],
                        legend='brief',
                        label="rolling "+ series["label"]
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
        args.output_filepath[df_idx].parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.output_filepath[df_idx], dpi=CONFIG_DPI, bbox_inches='tight')

if __name__ == "__main__":
    main()