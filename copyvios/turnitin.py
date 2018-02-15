# -*- coding: utf-8 -*-
from ast import literal_eval
import re

import requests

from .misc import parse_wiki_timestamp

__all__ = ['search_turnitin', 'TURNITIN_API_ENDPOINT']

TURNITIN_API_ENDPOINT = 'http://tools.wmflabs.org/eranbot/plagiabot/api.py'

def search_turnitin(page_title, lang):
    """ Search the Plagiabot database for Turnitin reports for a page.

    Keyword arguments:
    page_title -- string containing the page title
    lang       -- string containing the page's project language code

    Return a TurnitinResult (contains a list of TurnitinReports).
    """
    return TurnitinResult(_make_api_request(page_title, lang))

def _make_api_request(page_title, lang):
    """ Query the plagiabot API for Turnitin reports for a given page.
    """
    stripped_page_title = page_title.replace(' ', '_')
    api_parameters = {'action': 'suspected_diffs',
                      'page_title': stripped_page_title,
                      'lang': lang,
                      'report': 1}

    result = requests.get(TURNITIN_API_ENDPOINT, params=api_parameters)
    # use literal_eval to *safely* parse the resulting dict-containing string
    try:
        parsed_api_result = literal_eval(result.text)
    except (SyntaxError, ValueError):
        parsed_api_result = []
    return parsed_api_result

class TurnitinResult(object):
    """ Container class for TurnitinReports. Each page may have zero or
    more reports of plagiarism. The list will have multiple
    TurnitinReports if plagiarism has been detected for more than one
    revision.

    TurnitinResult.reports -- list containing >= 0 TurnitinReport items
    """
    def __init__(self, turnitin_data):
        """
        Keyword argument:
        turnitin_data -- plagiabot API result
        """
        self.reports = []
        for item in turnitin_data:
            report = TurnitinReport(
                item['diff_timestamp'], item['diff'], item['report'])
            self.reports.append(report)

    def __repr__(self):
        return str(self.__dict__)

class TurnitinReport(object):
    """ Contains data for each Turnitin report (one on each potentially
    plagiarized revision).

    TurnitinReport.reportid  -- Turnitin report ID, taken from plagiabot
    TurnitinReport.diffid    -- diff ID from Wikipedia database
    TurnitinReport.time_posted -- datetime of the time the diff posted
    TurnitinReport.sources   -- list of dicts with information on:
        percent -- percent of revision found in source as well
        words   -- number of words found in both source and revision
        url     -- url for the possibly-plagiarized source
    """
    def __init__(self, timestamp, diffid, report):
        """
        Keyword argument:
        timestamp  -- diff timestamp from Wikipedia database
        diffid     -- diff ID from Wikipedia database
        report     -- Turnitin report from the plagiabot database
        """
        self.report_data = self._parse_report(report)
        self.reportid = self.report_data[0]
        self.diffid = diffid
        self.time_posted = parse_wiki_timestamp(timestamp)

        self.sources = []
        for item in self.report_data[1]:
            source = {'percent': item[0],
                      'words': item[1],
                      'url': item[2]}
            self.sources.append(source)

    def __repr__(self):
        return str(self.__dict__)

    def _parse_report(self, report_text):
        # extract report ID
        report_id_pattern = re.compile(r'\?rid=(\d*)')
        report_id = report_id_pattern.search(report_text).groups()[0]

        # extract percent match, words, and URL for each source in the report
        extract_info_pattern = re.compile(
            r'\n\* \w\s+(\d*)\% (\d*) words at \[(.*?) ')
        results = extract_info_pattern.findall(report_text)

        return (report_id, results)
