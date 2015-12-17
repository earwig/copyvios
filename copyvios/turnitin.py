# -*- coding: utf-8 -*-
"""TODO: Docstrings, tests?, documentation of input/output formats (esp. nested data structures woe)"""

from ast import literal_eval
import re

import requests

__all__ = ['search_turnitin', 'TURNITIN_API_ENDPOINT']

TURNITIN_API_ENDPOINT = 'http://tools.wmflabs.org/eranbot/plagiabot/api.py'

def search_turnitin(page_title, lang):
    """ returns a list of tuples, one per report, each containing report id and data from the report"""
    turnitin_data = _parse_reports(_make_api_request('The quick brown fox jumps over the lazy dog', lang))
    turnitin_result = TurnitinResult(turnitin_data)
    return turnitin_result

def _make_api_request(page_title, lang):
    stripped_page_title = page_title.replace(' ', '_')
    api_parameters = {'action': 'suspected_diffs',
                      'page_title': stripped_page_title,
                      'lang': lang,
                      'report': 1}

    result = requests.get(TURNITIN_API_ENDPOINT, params=api_parameters)
    parsed_result = literal_eval(result.text)  # should be ok with encoding, content-type utf-8
    return parsed_result

def _parse_reports(turnitin_api_result):
    reports_data = []
    for item in turnitin_api_result:
        reports_data.append(_regex_magic(item['report']))
    return reports_data

def _regex_magic(report):
    # ~magic~
    report_id_pattern = re.compile(r'\?rid=(\d*)')
    report_id = report_id_pattern.search(report).groups()[0]

    extract_info_pattern = re.compile(r'\n\* \w\s+(\d*)\% (\d*) words at \[(.*?) ')
    results = extract_info_pattern.findall(report)

    return (report_id, results)

class TurnitinResult:
    def __init__(self, turnitin_data):
        self.reports = []
        for item in turnitin_data:
            report = TurnitinReport(item)
            self.reports.append(report)

    def __repr__(self):
        return str(self.__dict__)

class TurnitinReport:
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
