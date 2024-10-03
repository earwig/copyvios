from __future__ import annotations

__all__ = ["search_turnitin", "TURNITIN_API_ENDPOINT"]

import ast
import re
from dataclasses import dataclass
from datetime import datetime

import requests

from .misc import parse_wiki_timestamp

TURNITIN_API_ENDPOINT = "https://eranbot.toolforge.org/plagiabot/api.py"


def search_turnitin(page_title: str, lang: str) -> TurnitinResult:
    """
    Search the Plagiabot database for Turnitin reports for a page.
    """
    return TurnitinResult(_make_api_request(page_title, lang))


def _make_api_request(page_title: str, lang: str) -> list[dict]:
    """
    Query the plagiabot API for Turnitin reports for a given page.
    """
    stripped_page_title = page_title.replace(" ", "_")
    api_parameters = {
        "action": "suspected_diffs",
        "page_title": stripped_page_title,
        "lang": lang,
        "report": 1,
    }

    result = requests.get(TURNITIN_API_ENDPOINT, params=api_parameters, verify=False)
    # use literal_eval to *safely* parse the resulting dict-containing string
    try:
        parsed_api_result = ast.literal_eval(result.text)
    except (SyntaxError, ValueError):
        parsed_api_result = []
    return parsed_api_result


@dataclass
class TurnitinResult:
    """
    Container class for TurnitinReports.

    Each page may have zero or more reports of plagiarism. The list will have multiple
    TurnitinReports if plagiarism has been detected for more than one revision.
    """

    reports: list[TurnitinReport]

    def __init__(self, turnitin_data: list[dict]) -> None:
        """
        Keyword argument:
        turnitin_data -- plagiabot API result
        """
        self.reports = [
            TurnitinReport(item["diff_timestamp"], item["diff"], item["report"])
            for item in turnitin_data
        ]


@dataclass
class TurnitinReport:
    """
    Contains data for each Turnitin report.

    There is one report for each potentially plagiarized revision.

    TurnitinReport.reportid  -- Turnitin report ID, taken from plagiabot
    TurnitinReport.diffid    -- diff ID from Wikipedia database
    TurnitinReport.time_posted -- datetime of the time the diff posted
    TurnitinReport.sources   -- list of dicts with information on:
        percent -- percent of revision found in source as well
        words   -- number of words found in both source and revision
        url     -- url for the possibly-plagiarized source
    """

    reportid: str
    diffid: str
    time_posted: datetime
    sources: list[dict]

    def __init__(self, timestamp: str, diffid: str, report: str) -> None:
        """
        Keyword argument:
        timestamp  -- diff timestamp from Wikipedia database
        diffid     -- diff ID from Wikipedia database
        report     -- Turnitin report from the plagiabot database
        """
        self.reportid, results = self._parse_report(report)
        self.diffid = diffid
        self.time_posted = parse_wiki_timestamp(timestamp)

        self.sources = []
        for item in results:
            source = {"percent": item[0], "words": item[1], "url": item[2]}
            self.sources.append(source)

    def _parse_report(self, report_text: str) -> tuple[str, list[str]]:
        # extract report ID
        report_id_pattern = re.compile(r"\?rid=(\d*)")
        report_id_match = report_id_pattern.search(report_text)
        assert report_id_match, report_text
        report_id = report_id_match.group(1)

        # extract percent match, words, and URL for each source in the report
        extract_info_pattern = re.compile(r"\n\* \w\s+(\d*)\% (\d*) words at \[(.*?) ")
        results = extract_info_pattern.findall(report_text)

        return (report_id, results)
