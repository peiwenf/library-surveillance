#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import pandas as pd
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union
from tqdm import tqdm

from typing import List
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from constants import SINGLE_PAGE_AXE_RESULTS_FILENAME
from utils import clean_url
from constants_2022 import (
    ACCESS_EVAL_2022_STUDY_DATA,
    ACCESS_EVAL_2022_DATASET,
    DatasetFields,
)
###############################################################################

log = logging.getLogger(__name__)

###############################################################################

@dataclass_json
@dataclass
class TrackerMetrics:
    Email: List[str] = field(default_factory=list)
    EmailAggressive: List[str] = field(default_factory=list)
    Advertising: List[str] = field(default_factory=list)
    Content: List[str] = field(default_factory=list)
    Analytics: List[str] = field(default_factory=list)
    FingerprintingInvasive: List[str] = field(default_factory=list)
    FingerprintingGeneral: List[str] = field(default_factory=list)
    Social: List[str] = field(default_factory=list)
    Cryptomining: List[str] = field(default_factory=list)
    Disconnect: List[str] = field(default_factory=list)

    def reset(self):
        self.Email = []
        self.EmailAggressive = []
        self.Advertising = []
        self.Content = []
        self.Analytics = []
        self.FingerprintingInvasive = []
        self.FingerprintingGeneral = []
        self.Social = []
        self.Cryptomining = []
        self.Disconnect = []
    

def _recurse_axe_results(
    axe_results_dir: Path,
    metrics: TrackerMetrics,
    disconnect_json: Dict,
) -> TrackerMetrics:
    
    # Get this dirs result file
    this_dir_results = axe_results_dir / SINGLE_PAGE_AXE_RESULTS_FILENAME
    
    metrics = TrackerMetrics()
    metrics.reset()
    if this_dir_results.exists():
        with open(this_dir_results, "r") as open_f:
            this_dir_loaded_results = json.load(open_f)

        for track_link in this_dir_loaded_results['hosts']["requests"]["third_party"]:
            tracker = track_link.replace("www.", "")
            if ".google.com" not in track_link:
                parts = track_link.split(".")
                if len(parts) >= 3:
                    tracker = ".".join(parts[-2:])
            for category, entries in disconnect_json['categories'].items():
                for entry in entries:
                    for value_dict in entry.values():
                        for url, values in value_dict.items():
                            if tracker in url:
                                getattr(metrics, category).append(track_link)
                            for value in values:
                                if tracker in value:
                                    getattr(metrics, category).append(track_link)
        metrics.Email, metrics.Content, metrics.Analytics, metrics.FingerprintingGeneral, metrics.Social, metrics.Disconnect = [
            list(set(val for val in getattr(metrics, attr))) for attr in [
                'Email', 'Content', 'Analytics', 'FingerprintingGeneral', 'Social', 'Disconnect']]
    
    return metrics

def _convert_metrics_to_expanded_data(
    metrics: TrackerMetrics,
) -> Dict[str, int]:

    return {
        f"Email": metrics.Email,
        f"EmailAggressive": metrics.EmailAggressive,
        f"Advertising": metrics.Advertising,
        f"Content": metrics.Content,
        f"Analytics": metrics.Analytics,
        f"FingerprintingInvasive": metrics.FingerprintingInvasive,
        f"FingerprintingGeneral": metrics.FingerprintingGeneral,
        f"Social": metrics.Social,
        f"Cryptomining": metrics.Cryptomining,
        f"Disconnect": metrics.Disconnect,
    }


def combine_library_data_with_axe_results(
    library_data: Union[str, Path, pd.DataFrame],
    lib_scraping_results: Union[str, Path],
) -> pd.DataFrame:
    """
    Combine library data CSV (or in memory DataFrame) with the blacklight results for each
    library website.

    Parameters
    ----------
    library_data: Union[str, Path, pd.DataFrame]
        The path to, or the in-memory dataframe, containing basic library data.
        This CSV or dataframe should contain two columns "Homepage" and "Catalog"
        that can be used to find the associated directory of blacklight results for that
        library.
    lib_scraping_results: Union[str, Path]
        The path to the directory that contains sub-directories for each library
        website's blacklight results. 

    Returns
    -------
    full_data: pd.DataFrame
        The original library data, the summed trackers counts for each library
        website combined into a single dataframe.

    Finally, any `https://` or `http://` is dropped from the campaign url.
    I.e. in the spreadsheet the value is `https://website.org` but the associated
    directory should be: `data/website.org`
    """
    # Confirm paths
    lib_scraping_results = Path(lib_scraping_results).resolve(
        strict=True
    )

    if isinstance(library_data, (str, Path)):
        library_data = Path(library_data).resolve(strict=True)
        library_data = pd.read_csv(library_data)

    # Confirm axe scraping results is dir
    if not lib_scraping_results.is_dir():
        raise NotADirectoryError(lib_scraping_results)
    
    disconnect_dir = ACCESS_EVAL_2022_STUDY_DATA / "services.json"
    if disconnect_dir.exists():
        with open(disconnect_dir, "r") as open_f:
            disconnect_json = json.load(open_f)

    # Iter election data and create List of expanded dicts with added
    expanded_data = []
    for _, row in tqdm(library_data.iterrows()):
        if isinstance(row[DatasetFields.homepage_url], str):
            cleaned_url = clean_url(row[DatasetFields.homepage_url])
            access_eval = lib_scraping_results / cleaned_url
        else:
            access_eval = None

        # if not access_eval == None:
        if access_eval != None and access_eval.exists():
            access_eval = Path(access_eval).resolve(strict=True)
            if not access_eval.is_dir():
                raise NotADirectoryError(access_eval)
            # Run metric generation
            access_eval_metrics = _recurse_axe_results(
                access_eval, TrackerMetrics, disconnect_json
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
            row.homepage_url = None
            expanded_data.append(
                {
                    # Original row details with unworking links removed
                    **row,
                }
            )

    log.info(
        f"Dropped {len(library_data) - len(expanded_data)} rows from dataset "
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