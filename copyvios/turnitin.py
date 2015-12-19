# -*- coding: utf-8 -*-
from ast import literal_eval
import re

import requests

__all__ = ['search_turnitin', 'TURNITIN_API_ENDPOINT']

TURNITIN_API_ENDPOINT = 'http://tools.wmflabs.org/eranbot/plagiabot/api.py'

def search_turnitin(page_title, lang):
    """ Search the Plagiabot database for Turnitin reports for a page.

    Keyword arguments:
    page_title -- string containing the page title
    lang       -- string containing the page's project language code

    Return a TurnitinResult (containing a list of TurnitinReports, with
    report ID and source data).
    """
    turnitin_data = _parse_plagiabot_result(_make_api_request(
        page_title, lang))
    turnitin_result = TurnitinResult(turnitin_data)
    return turnitin_result

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
    parsed_api_result = literal_eval(result.text)
    return parsed_api_result

def _parse_plagiabot_result(turnitin_api_result):
    result_data = []
    for item in turnitin_api_result:
        result_data.append(_parse_report(item['report']))
    return result_data

def _parse_report(report):
    # extract report ID
    report_id_pattern = re.compile(r'\?rid=(\d*)')
    report_id = report_id_pattern.search(report).groups()[0]

    # extract percent match, words, and URL for each source in the report
    extract_info_pattern = re.compile(r'\n\* \w\s+(\d*)\% (\d*) words at \[(.*?) ')
    results = extract_info_pattern.findall(report)

    return (report_id, results)

class TurnitinResult:
    """ Container class for TurnitinReports. Each page may have zero or
    more reports of plagiarism. The list will have multiple
    TurnitinReports if plagiarism has been detected for more than one
    revision.

    TurnitinResult.reports -- list containing >= 0 TurnitinReport items
    """
    def __init__(self, turnitin_data):
        """
        Keyword argument:
        turnitin_data -- list of tuples with data on each report; see
                         TurnitinReport.__init__ for the contents.
        """
        self.reports = []
        for item in turnitin_data:
            report = TurnitinReport(item)
            self.reports.append(report)

    def __repr__(self):
        return str(self.__dict__)

class TurnitinReport:
    """ Contains data for each Turnitin report (one on each potentially
    plagiarized revision).

    TurnitinReport.reportid -- Turnitin report ID, taken from plagiabot
    TurnitinReport.sources -- list of dicts with information on:
        percent -- percent of revision found in source as well
        words   -- number of words found in both source and revision
        url     -- url for the possibly-plagiarized source
    """
    def __init__(self, data):
        """
        Keyword argument:
        data -- tuple containing report data. All values are strings.
            data[0] -- turnitin report ID
            data[1] -- list of tuples with data on each source in the
                       report
               data[<index>][0] -- percent of revision found in source
               data[<index>][1] -- number of words matching the source
               data[<index>][2] -- url for the matched source
        """
        self.reportid = data[0]

        self.sources = []
        for item in data[1]:
            source = {'percent': item[0],
                      'words': item[1],
                      'url': item[2]}
            self.sources.append(source)

    def __repr__(self):
        return str(self.__dict__)
