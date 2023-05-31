#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging


import altair as alt
import pandas as pd

from constants_2022 import DatasetFields
from core_2022 import load_access_eval_2022_dataset

###############################################################################

PLOTTING_DIR = Path("plots/").resolve()
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)4s: %(module)s:%(lineno)4s %(asctime)s] %(message)s",
)
log = logging.getLogger(__name__)

###############################################################################

def _plot_and_fig_text(
    data: pd.DataFrame,
    plot_cols: List[str],
    fig_text_prefix: str,
    subset_name: str,
    column: Optional[alt.Column] = None,
    consistent_scale: bool = False,
) -> None:
    
    chart = alt.hconcat(spacing=40)
    for col in plot_cols:
        scale = alt.Scale(
            domain=(
                data[col].min(),
                data[col].max(),
            ),
            # domain=(
            #     0,
            #     250,
            # ),
            # padding=1,
            )

        if column is None:
            chart |= (
                alt.Chart(data)
                .mark_boxplot()
                .encode(
                    y=alt.Y(
                        col,
                        scale=scale,
                    )
                )
            )
        else:
            chart |= (
                alt.Chart(data)
                .mark_boxplot()
                .encode(
                    y=alt.Y(
                        col,
                        scale=scale,
                    ),
                    column=column,
                )
            )
        fig_text_prefix += (
            f" {col} "
            f"mean: {round(data[col].mean(), 2)}, "
            f"std: {round(data[col].std(), 2)}, "
            f"min: {round(data[col].min(), 2)}, "
            f"max: {round(data[col].max(), 2)}."
            f"median: {round(data[col].median(), 2)}."
            f"major: {round(data[col].quantile([0.25, 0.75]), 2)}."
        )
    chart.properties(title="Campaign Website Content")

    # Save fig and text
    fig_save_path = PLOTTING_DIR / f"{subset_name}.png"
    fig_save_path.parent.mkdir(parents=True, exist_ok=True)
    chart.save(str(fig_save_path))
    with open(fig_save_path.with_suffix(".txt"), "w") as open_f:
        open_f.write(fig_text_prefix)


def plot_homepage_stats(
    data: Optional[pd.DataFrame] = None,
    subset_name: str = "",
    keep_cols: List[str] = [],
    plot_kwargs: Dict[str, Any] = {},
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    score_cols = [
        DatasetFields.number_of_total_trackers_homepage,
        DatasetFields.behaviour_event_listeners_homepage,
        DatasetFields.cookies_homepage,
        DatasetFields.third_party_trackers_homepage,
        DatasetFields.canvas_fingerprinters_homepage,
        DatasetFields.canvas_font_fingerprinters_homepage,
        DatasetFields.key_logging_homepage,
        DatasetFields.session_recorders_homepage,
    ]

    # Create content plots
    _plot_and_fig_text(
        data=data[[*score_cols, *keep_cols]],
        plot_cols=score_cols,
        fig_text_prefix=(
            "Distributions for key content statistics "
            "gathered while scraping campaign websites."
        ),
        subset_name=f"homepage-content-stats",
        **plot_kwargs,
    )

def plot_catalog_stats(
    data: Optional[pd.DataFrame] = None,
    subset_name: str = "",
    keep_cols: List[str] = [],
    plot_kwargs: Dict[str, Any] = {},
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    score_cols = [
        DatasetFields.number_of_total_trackers_catalog,
        DatasetFields.behaviour_event_listeners_catalog,
        DatasetFields.cookies_catalog,
        DatasetFields.third_party_trackers_catalog,
        DatasetFields.canvas_fingerprinters_catalog,
        DatasetFields.canvas_font_fingerprinters_catalog,
        DatasetFields.key_logging_catalog,
        DatasetFields.session_recorders_catalog,
    ]

    # Create content plots
    _plot_and_fig_text(
        data=data[[*score_cols, *keep_cols]],
        plot_cols=score_cols,
        fig_text_prefix=(
            "Distributions for key content statistics "
            "gathered while scraping campaign websites."
        ),
        subset_name=f"catalog-content-stats",
        **plot_kwargs,
    )

def plot_summary_stats(
    data: Optional[pd.DataFrame] = None,
    subset_name: str = "",
    keep_cols: List[str] = [],
    plot_kwargs: Dict[str, Any] = {},
) -> None:
    """
    Input data should be the "flattened" dataset.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    score_cols = [
        DatasetFields.number_of_total_trackers_homepage,
        DatasetFields.number_of_total_trackers_catalog,
    ]

    # Create content plots
    _plot_and_fig_text(
        data=data[[*score_cols, *keep_cols]],
        plot_cols=score_cols,
        fig_text_prefix=(
            "Distributions for key content statistics "
            "gathered while scraping campaign websites."
        ),
        subset_name=f"{subset_name}content-stats",
        **plot_kwargs,
    )


def plot_state_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    # Drop any locations with less than two campaigns (originally <= 2)
    location_counts = data[DatasetFields.state].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    log.info(top_5_locations)
    data = data[data[DatasetFields.state].isin(top_5_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="location-split-",
        keep_cols=[DatasetFields.state],
        plot_kwargs={"column": alt.Column(DatasetFields.state, spacing=60)},
    )


def plot_automation_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:

    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    location_counts = data[DatasetFields.current_automation].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    data = data[data[DatasetFields.current_automation].isin(top_5_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="current-automation-split-",
        keep_cols=[DatasetFields.current_automation],
        plot_kwargs={"column": alt.Column(DatasetFields.current_automation, spacing=60)},
    )


def plot_interface_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    location_counts = data[DatasetFields.discovery_interface].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    log.info(top_5_locations)
    data = data[data[DatasetFields.discovery_interface].isin(top_5_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="discovery-interface-split-",
        keep_cols=[DatasetFields.discovery_interface],
        plot_kwargs={
            "column": alt.Column(DatasetFields.discovery_interface, spacing=60)
        },
    )

def plot_ID_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    location_counts = data[DatasetFields.item_ID].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    log.info(top_5_locations)
    data = data[data[DatasetFields.item_ID].isin(top_5_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="item-ID-split-",
        keep_cols=[DatasetFields.item_ID],
        plot_kwargs={
            "column": alt.Column(DatasetFields.item_ID, spacing=60)
        },
    )

def plot_content_based_summary_stats(
    data: Optional[pd.DataFrame] = None,
) -> None:
    
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    location_counts = data[DatasetFields.web_content].value_counts()
    top_5_locations = location_counts.nlargest(5).index
    log.info(top_5_locations)
    data = data[data[DatasetFields.item_ID].isin(top_5_locations)]

    # Plot basic stats
    plot_summary_stats(
        data,
        subset_name="web-content-split-",
        keep_cols=[DatasetFields.item_ID],
        plot_kwargs={
            "column": alt.Column(DatasetFields.item_ID, spacing=60)
        },
    )