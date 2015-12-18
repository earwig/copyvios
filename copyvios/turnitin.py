# -*- coding: utf-8 -*-
"""TODO: Docstrings, tests?, documentation of input/output formats (esp. nested data structures)"""

from ast import literal_eval
import re

import requests

__all__ = ['search_turnitin', 'TURNITIN_API_ENDPOINT']

TURNITIN_API_ENDPOINT = 'http://tools.wmflabs.org/eranbot/plagiabot/api.py'

def search_turnitin(page_title, lang):
    """ returns a TurnitinResult, containing a list of TurnitinReport items, each containing report id and a list of dicts with data from the report"""
    turnitin_data = _parse_plagiabot_result(_make_api_request(
        'The quick brown fox jumps over the lazy dog', lang))  # FIXME: replace with page_title when the earwigbot dev setup is working properly
    turnitin_result = TurnitinResult(turnitin_data)
    return turnitin_result

def _make_api_request(page_title, lang):
    """ Query the plagiabot API for Turnitin reports for a given page
    page_title : string containing title of the page in question
    lang : string containing language code for the current project
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
        reports_data.append(_parse_report(item['report']))
    return result_data

def _parse_report(report):
    """ Given the "report" bit from the plagiabot API, extract the report ID and the percent/words/url
    """
    # ~magic~
    report_id_pattern = re.compile(r'\?rid=(\d*)')
    report_id = report_id_pattern.search(report).groups()[0]

    extract_info_pattern = re.compile(r'\n\* \w\s+(\d*)\% (\d*) words at \[(.*?) ')
    results = extract_info_pattern.findall(report)

    return (report_id, results)

class TurnitinResult:
    """ Container class for TurnitinReports. Each page may have zero or
    more reports of plagiarism, if plagiarism has been detected for
    different revisions.

    TurnitinResult.reports : list containing zero or more TurnitinReports
    """
    def __init__(self, turnitin_data):
        self.reports = []
        for item in turnitin_data:
            report = TurnitinReport(item)
            self.reports.append(report)

    def __repr__(self):
        return str(self.__dict__)

class TurnitinReport:
    """ Contains data for each Turnitin report.
    TurnitinReport.sources : list of dicts with info from each source
    TurnitinReport.reportid : Turnitin report ID, taken from plagiabot
    """
    def __init__(self, data):
        self.reportid = data[0]

        self.sources = []
        for item in data[1]:
            source = {'percent': item[0],
                      'words': item[1],
                      'url': item[2]}
            self.sources.append(source)

    def __repr__(self):
        return str(self.__dict__)
