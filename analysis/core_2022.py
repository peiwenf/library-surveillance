#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

import numpy as np
import pandas as pd
from dataclasses_json import dataclass_json
from scipy import stats as sci_stats
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import FirefoxOptions
from textstat import flesch_reading_ease
from tqdm import tqdm

from constants import SINGLE_PAGE_AXE_RESULTS_FILENAME
from utils import clean_url
from constants_2022 import (
    ACCESS_EVAL_2022_DATASET,
    DatasetFields,
)

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

@dataclass_json
@dataclass
class RunningMetrics:
    behaviour_event_listeners: int = 0
    canvas_fingerprinters: int = 0
    canvas_font_fingerprinters: int = 0
    cookies: int = 0
    fb_pixel_events: int = 0
    key_logging: int = 0
    session_recorders: int = 0
    third_party_trackers: int = 0
    google: int = 0
    google_analytics: int = 0
    facebook: int = 0

    def reset(self):
        self.behaviour_event_listeners = 0
        self.canvas_fingerprinters = 0
        self.canvas_font_fingerprinters = 0
        self.cookies = 0
        self.fb_pixel_events = 0
        self.key_logging = 0
        self.session_recorders = 0
        self.third_party_trackers = 0
        self.google = 0
        self.google_analytics = 0
        self.facebook = 0



@dataclass_json
@dataclass
class CompiledMetrics:
    behaviour_event_listeners: int = 0
    canvas_fingerprinters: int = 0
    canvas_font_fingerprinters: int = 0
    cookies: int = 0
    fb_pixel_events: int = 0
    key_logging: int = 0
    session_recorders: int = 0
    third_party_trackers: int = 0
    google: int = 0
    google_analytics: int = 0
    facebook: int = 0


###############################################################################

def _recurse_axe_results(
    axe_results_dir: Path,
    metrics: RunningMetrics,
) -> RunningMetrics:

    # Get this dirs result file
    this_dir_results = axe_results_dir / SINGLE_PAGE_AXE_RESULTS_FILENAME
    
    metrics = RunningMetrics()
    metrics.reset()
    if this_dir_results.exists():
        with open(this_dir_results, "r") as open_f:
            this_dir_loaded_results = json.load(open_f)

        # get the number of different trackers
        sec_layer = ["canvas_fingerprinters", "canvas_font_fingerprinters", "behaviour_event_listeners"]
        for key in this_dir_loaded_results['reports'].keys():
            if key in sec_layer:
                for sub_key in this_dir_loaded_results['reports'][key].keys():
                    current_count = getattr(metrics, key)
                    setattr(
                        metrics,
                        key,
                        current_count + 
                        len(this_dir_loaded_results['reports'][key][sub_key]),
                    )
            else:
                setattr(
                    metrics,
                    key,
                    len(this_dir_loaded_results['reports'][key]),
                )
        
        tracker_num = len(this_dir_loaded_results['reports']["third_party_trackers"])
        for i in range(0, tracker_num):
            if "google-analytics" in this_dir_loaded_results['reports']["third_party_trackers"][i]['url']:
                current_count = getattr(metrics, "google_analytics")
                setattr(
                    metrics,
                    "google_analytics",
                    current_count + 1,
                )
            elif "google" in this_dir_loaded_results['reports']["third_party_trackers"][i]['url']:
                current_count = getattr(metrics, "google")
                setattr(
                    metrics,
                    "google",
                    current_count + 1,
                )
            elif "facebook" in this_dir_loaded_results['reports']["third_party_trackers"][i]['url']:
                current_count = getattr(metrics, "facebook")
                setattr(
                    metrics,
                    "facebook",
                    current_count + 1,
                )
    
    return metrics


def process_axe_evaluations_and_extras(
    axe_results_dir: Union[str, Path],
) -> CompiledMetrics:
    """
    Process all blacklight evaluations 

    Parameters
    ----------
    axe_results_dir: Union[str, Path]
        The directory for a specific website that has been processed using the access
        eval scraper.

    Returns
    -------
    metrics: CompiledMetrics
        The counts of all trackers types
    """
    # Handle path and dir checking
    axe_results_dir = Path(axe_results_dir).resolve(strict=True)
    if not axe_results_dir.is_dir():
        raise NotADirectoryError(axe_results_dir)

    # Process
    parsed_metrics = _recurse_axe_results(
        axe_results_dir, RunningMetrics
    )

    return CompiledMetrics(
        behaviour_event_listeners = parsed_metrics.behaviour_event_listeners,
        canvas_fingerprinters = parsed_metrics.canvas_fingerprinters,
        canvas_font_fingerprinters = parsed_metrics.canvas_font_fingerprinters,
        cookies = parsed_metrics.cookies,
        fb_pixel_events = parsed_metrics.fb_pixel_events,
        key_logging = parsed_metrics.key_logging,
        session_recorders = parsed_metrics.session_recorders,
        third_party_trackers = parsed_metrics.third_party_trackers,
        google = parsed_metrics.google,
        google_analytics = parsed_metrics.google_analytics,
        facebook = parsed_metrics.facebook
    )


def _convert_metrics_to_expanded_data(
    metrics: CompiledMetrics,
) -> Dict[str, int]:

    return {
        **track_types,
        f"number_of_pages": metrics.pages,
        f"number_of_total_trackers": (
            metrics.behaviour_event_listeners
            + metrics.canvas_fingerprinters
            + metrics.canvas_font_fingerprinters
            + metrics.cookies
            + metrics.fb_pixel_events
            + metrics.key_logging
            + metrics.session_recorders
            + metrics.third_party_trackers
        ),
        f"behaviour_event_listeners": metrics.behaviour_event_listeners,
        f"canvas_fingerprinters": metrics.canvas_fingerprinters,
        f"canvas_font_fingerprinters": metrics.canvas_font_fingerprinters,
        f"cookies": metrics.cookies,
        f"fb_pixel_events": metrics.fb_pixel_events,
        f"key_logging": metrics.key_logging,
        f"session_recorders": metrics.session_recorders,
        f"third_party_trackers": metrics.third_party_trackers,
        f"google": metrics.google,
        f"google_analytics": metrics.google_analytics,
        f"facebook": metrics.facebook
    }


def combine_election_data_with_axe_results(
    election_data: Union[str, Path, pd.DataFrame],
    axe_scraping_results: Union[str, Path],
) -> pd.DataFrame:
    """
    Combine election data CSV (or in memory DataFrame) with the blacklight results for each
    campaign website.

    Parameters
    ----------
    election_data: Union[str, Path, pd.DataFrame]
        The path to, or the in-memory dataframe, containing basic election data.
        This CSV or dataframe should contain a column "campaign_website_url"
        that can be used to find the associated directory of axe results for that
        campaigns website.
    axe_scraping_results: Union[str, Path]
        The path to the directory that contains sub-directories for each campaign
        website's blacklight results. 

    Returns
    -------
    full_data: pd.DataFrame
        The original election data, the summed trackers counts for each campaign
        website combined into a single dataframe.

    Additionally, if the provided campaign website url is missing, the site is
    skipped / dropped from the expanded dataset.

    Finally, any `https://` or `http://` is dropped from the campaign url.
    I.e. in the spreadsheet the value is `https://website.org` but the associated
    directory should be: `data/website.org`
    """
    # Confirm paths
    axe_scraping_results = Path(axe_scraping_results).resolve(
        strict=True
    )

    if isinstance(election_data, (str, Path)):
        election_data = Path(election_data).resolve(strict=True)
        election_data = pd.read_csv(election_data)

    # Confirm axe scraping results is dir
    if not axe_scraping_results.is_dir():
        raise NotADirectoryError(axe_scraping_results)

    # Iter election data and create List of expanded dicts with added
    expanded_data = []
    for _, row in tqdm(election_data.iterrows()):
        if isinstance(row[DatasetFields.campaign_website_url], str):
            cleaned_url = clean_url(row[DatasetFields.campaign_website_url])
            access_eval = axe_scraping_results / cleaned_url
        else:
            access_eval = None

        # if not access_eval == None:
        if access_eval != None and access_eval.exists():
            # Run metric generation
            access_eval_metrics = process_axe_evaluations_and_extras(
                access_eval,
            )

            # Combine and merge to expanded data
            expanded_data.append(
                {
                    # Original row details
                    **row,
                    # axe-report
                    **_convert_metrics_to_expanded_data(
                        access_eval_metrics,
                    ),
                }
            )
        else:
            row.campaign_website_url = None
            expanded_data.append(
                {
                    # Original row details with unworking links removed
                    **row,
                }
            )

    log.info(
        f"Dropped {len(election_data) - len(expanded_data)} rows from dataset "
        f"because they were missing a result directory."
    )
    return pd.DataFrame(expanded_data)


def load_access_eval_2022_dataset(
    path: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Load the default access eval 2022 dataset or a provided custom dataset
    and add all computed fields.

    Parameters
    ----------
    path: Optional[Union[str, Path]]
        An optional path for custom data to load.
        Default: None (load official 2022 access eval dataset)

    Returns
    -------
    data: pd.DataFrame
        The loaded dataframe object with all extra computed fields added.
    """

    if path is None:
        path = ACCESS_EVAL_2022_DATASET

    # Load base data
    data = pd.read_csv(ACCESS_EVAL_2022_DATASET)
    
    # Replace the NaN with 0 
    for col in data.columns:
        if "error-type_" in col:
            data[col] = data[col].fillna(0)

    # Collect error type cols with a value above 0 at the 25th percentile
    common_error_cols = []
    for col in data.columns:
        if "error-type_" in col and data[col].quantile(0.75) > 0:
            common_error_cols.append(col)

    # Create norm cols
    for common_error_col in common_error_cols:
        error_type = common_error_col
        avg_error_type_col_name = f"avg_{error_type}_per_page"
        norm_col = DatasetFields.number_of_pages

        # Norm
        data[avg_error_type_col_name] = data[common_error_col] / data[norm_col]

    return data

def get_crucial_stats(
    data: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Generate statistics we found useful in the 2022 paper.
    """
    # Load default data
    if data is None:
        data = load_access_eval_2022_dataset()

    # Generate demographics and tables
    with open("overall-stats.txt", "w") as open_f:
        open_f.write(
            data[[ num_pages_col, avg_errs_per_page_col]]
            .agg([np.mean, np.std])
            .to_latex()
        )

    print("Number of sites for this run:", len(data))

    # Get majority of ease of reading
    stats["majority trackers"] = data[DatasetFields.number_of_total_trackers].quantile(
        [0.25, 0.75]
    )
    stats["trackers | mean and std"] = {
        "mean": data[DatasetFields.number_of_total_trackers].mean(),
        "std": data[DatasetFields.number_of_total_trackers].std(),
    }

    # Get trends for election outcome
    winning_races = data[data[DatasetFields.election_result] == "Won"]
    losing_races = data[data[DatasetFields.election_result] == "Lost"]
    stats["win vs lose | tackers"] = sci_stats.ttest_ind(
        winning_races[number_of_total_trackers],
        losing_races[number_of_total_trackers],
        equal_var=False,
    )

    # Clean stats
    for k, v in stats.items():
        if isinstance(
            v,
            (
                sci_stats.stats.Ttest_indResult,
                sci_stats.stats.F_onewayResult,
                sci_stats.stats.Ttest_relResult,
            ),
        ):
            stats[k] = {"statistic": v.statistic, "pvalue": v.pvalue}
        elif isinstance(v, pd.Series):
            stats[k] = v.tolist()

    return stats
