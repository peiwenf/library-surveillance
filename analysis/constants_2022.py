#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Callable, NamedTuple

###############################################################################


ACCESS_EVAL_2022_STUDY_REPORTS = Path(__file__).parent / "reports_2022"
ACCESS_EVAL_2022_STUDY_DATA = Path(__file__).parent / "data_2022"

ACCESS_EVAL_2022_ELECTION_RESULTS = ACCESS_EVAL_2022_STUDY_DATA / "public_lib_purpose.csv"
ACCESS_EVAL_2022_EVALS_ZIP = (
    ACCESS_EVAL_2022_STUDY_REPORTS / "Homepage.zip"
)

ACCESS_EVAL_2022_EVALS_UNPACKED = Path("unpacked-eval-results")

ACCESS_EVAL_2022_DATASET = ACCESS_EVAL_2022_STUDY_DATA / "public_lib_purpose_total.csv"
###############################################################################


class ComputedField(NamedTuple):
    name: str
    func: Callable


class DatasetFields:
    """
    This class stores all of the headers for the analysis dataset.

    Each header will have a description and some examples.
    Use this class as a data dictionary.
    """

    state = "State"
    """
    str: The State where the library is located.

    Examples
    --------
    - "Alabama"
    - "Arizona"
    """

    location = "location"
    """
    str: The District, County, or City for the library.

    Examples
    --------
    - "Orange"
    - "Little Rock"
    """

    homepage_url = "Homepage"
    catalog_url = "Catalog"
    """
    str: The urls for the library's homepage and catalog page.

    Examples
    --------
    - "https://www.google.com"
    - "https://jacksonmaxfield.github.io"
    """

    number_of_total_trackers_homepage = "number_of_total_trackers_homepage"
    number_of_total_trackers_catalog = "number_of_total_trackers_catalog"
    """
    int: The total tracker that blacklight detects in the body of the webpage

    Examples
    --------
    - "29"
    - "450"
    """

    behaviour_event_listeners_homepage = "behaviour_event_listeners_homepage"
    canvas_fingerprinters_homepage = "canvas_fingerprinters_homepage"
    canvas_font_fingerprinters_homepage = "canvas_font_fingerprinters_homepage"
    cookies_homepage = "cookies_homepage"
    fb_pixel_events_homepage = "fb_pixel_events_homepage"
    key_logging_homepage = "key_logging_homepage"
    session_recorders_homepage = "session_recorders_homepage"
    third_party_trackers_homepage = "third_party_trackers_homepage"
    
    behaviour_event_listeners_catalog = "behaviour_event_listeners_catalog"
    canvas_fingerprinters_catalog = "canvas_fingerprinters_catalog"
    canvas_font_fingerprinters_catalog = "canvas_font_fingerprinters_catalog"
    cookies_catalog = "cookies_catalog"
    fb_pixel_events_catalog = "fb_pixel_events_catalog"
    key_logging_catalog = "key_logging_catalog"
    session_recorders_catalog = "session_recorders_catalog"
    third_party_trackers_catalog = "third_party_trackers_catalog"
    """
    int: The count of different types of tracker that blacklight detects 
    in the body of the webpage

    Examples
    --------
    - "29"
    - "300"
    """

    google_homepage = 'google_homepage'
    google_analytics_homepage = 'google_analytics_homepage'
    facebook_homepage = 'facebook_homepage'
    google_catalog = 'google_catalog'
    google_analytics_catalog = 'google_analytics_catalog'
    facebook_catalog = 'facebook_catalog'
    """
    int: The count of specific third party trackers caclucated 
    based on the black light result, where "google" also counts "google_analytics"
    and "facebook" also counts "fb_pixel_events"

    Examples
    --------
    - "29"
    - "300"
    """

    current_automation = "Current Automation System Name"
    discovery_interface = "Discovery Interface Name"
    item_ID = "Item ID Type Name"
    web_content = "Web Content Magement Name"

    """
    str: The vendors for the most frequently used technologies

    Examples
    --------
    - "Polaris"
    - "PLUS"
    """