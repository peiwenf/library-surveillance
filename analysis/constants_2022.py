#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Callable, NamedTuple

###############################################################################


ACCESS_EVAL_2022_STUDY_REPORTS = Path(__file__).parent / "reports_2022"
ACCESS_EVAL_2022_STUDY_DATA = Path(__file__).parent / "data_2022"

ACCESS_EVAL_2022_ELECTION_RESULTS = ACCESS_EVAL_2022_STUDY_DATA / "total_2022_blacklight_0.9.csv"
ACCESS_EVAL_2022_EVALS_ZIP = (
    ACCESS_EVAL_2022_STUDY_REPORTS / "combined.zip"
)

ACCESS_EVAL_2022_EVALS_UNPACKED = Path("unpacked-eval-results")

ACCESS_EVAL_2022_DATASET = ACCESS_EVAL_2022_STUDY_DATA / "total_2022_blacklight_0.9_google.csv"
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

    state = "state"
    """
    str: The State where the election is held.

    Examples
    --------
    - "Alabama"
    - "Arizona"
    """

    location = "location"
    """
    str: The District or County for the election.

    Examples
    --------
    - "Alabama 1st"
    - "Little Rock"
    """

    campaign_website_url = "campaign_website_url"
    """
    str: The public URL for the campaign website.

    Examples
    --------
    - "https://www.google.com"
    - "https://jacksonmaxfield.github.io"
    """

    electoral_position = "electoral_position"
    """
    str: The position the candidate was running for.

    Examples
    --------
    - "Mayor"
    - "Council"
    """

    electoral_level= "electoral_level"
    """
    str: The electoral level of the race.

    Examples
    --------
    - "Federal"
    - "State"
    - "Special District"
    - "County"
    - "City"
    - "City/County"
    """

    electoral_level_3= "electoral_level_3"
    """
    str: The electoral level of the races that categorized into
    three levels only(Federal, State, and Local).

    Examples
    --------
    - "Federal"
    - "State"
    - "Local"
    """

    electoral_branch = "electoral_branch"
    """
    str: The electoral branch of the races.

    Examples
    --------
    - "Judicial"
    - "Legisilative"
    - "Executive"
    """

    election_result = "election_result"
    """
    str: Categorical value for is the candidate won (or progressed) or not.

    Examples
    --------
    - "Won"
    - "Lost"

    Notes
    -----
    Pulled from external data source.
    """

    number_of_votes_for_candidate = "number_of_votes_for_candidate"
    """
    int: The number of votes the candidate ultimately received.

    Examples
    --------
    - 12345
    - 2468

    Notes
    -----
    Pulled from external data source.
    """

    number_of_votes_for_race = "number_of_votes_for_race"
    """
    int: The total number of votes returned in the election.

    Examples
    --------
    - 123456
    - 24680

    Notes
    -----
    Pulled from external data source.
    """

    vote_share = "vote_share"
    """
    float: The number of votes the candidate received over the number of votes possible.

    Examples
    --------
    - 0.21
    - 0.47
    """

    party = "party"
    """
    str: The party of the candidate.

    Examples
    --------
    - "Democratic Party"
    - "Independent"
    """

    competitiveness = 'competitiveness'
    """
    float: The distance between the vote share of the candidate and 0.5

    Examples
    --------
    - "0.1"
    - "0.5"
    """
    
    number_of_total_trackers = "number_of_total_trackers"
    """
    int: The total tracker that blacklight detects in the body of the webpage

    Examples
    --------
    - "29"
    - "450"
    """

    behaviour_event_listeners = "behaviour_event_listeners"
    canvas_fingerprinters = "canvas_fingerprinters"
    canvas_font_fingerprinters = "canvas_font_fingerprinters"
    cookies = "cookies"
    fb_pixel_events = "fb_pixel_events"
    key_logging = "key_logging"
    session_recorders = "session_recorders"
    third_party_trackers = "third_party_trackers"
    """
    int: The count of different types of tracker that blacklight detects 
    in the body of the webpage

    Examples
    --------
    - "29"
    - "300"
    """

    google = 'google'
    google_analytics = 'google_analytics'
    facebook = 'facebook'
    """
    int: The count of specific third party trackers caclucated 
    based on the black light result, where "google" also counts "google_analytics"
    and "facebook" also counts "fb_pixel_events"

    Examples
    --------
    - "29"
    - "300"
    """