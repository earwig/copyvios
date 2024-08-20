#!/bin/env python3
import argparse
import re
import sqlite3

REGEX = re.compile(
    r'^'
    r'{address space usage: (?P<used_bytes>-?\d+) bytes/(?P<used_mb>\w+)} '
    r'{rss usage: (?P<rss_bytes>-?\d+) bytes/(?P<rss_mb>\w+)} '
    r'\[pid: (?P<pid>\d+)\|app: -\|req: -/-\] (?P<ip>[0-9.]+) \(-\) '
    r'{(?P<vars>\d+) vars in (?P<var_bytes>\d+) bytes} '
    r'\[(?P<date>[0-9A-Za-z: ]+)\] (?P<method>\w+) (?P<url>.*?) => '
    r'generated (?P<resp_bytes>\d+) bytes in (?P<msecs>\d+) msecs '
    r'\((- http://hasty.ai)?(?P<proto>[A-Z0-9/.]+) (?P<status>\d+)\) '
    r'(?P<headers>\d+) headers in (?P<header_bytes>\d+) bytes '
    r'\((?P<switches>\d+) switches on core (?P<core>\d+)\) '
    r'(?P<agent>.*?)'
    r'( (?P<referer>https?://[^ ]*?))?( -)?( http(://|%3A%2F%2F)hasty\.ai)?'
    r'$'
)

def save_logs(logs):
    columns = sorted(REGEX.groupindex, key=lambda col: REGEX.groupindex[col])
    conn = sqlite3.Connection('logs.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS logs(%s)' % ', '.join(columns))
    cur.executemany('INSERT INTO logs VALUES (%s)' % ', '.join(['?'] * len(columns)),
                    [[log[col] for col in columns] for log in logs])
    conn.commit()
    conn.close()

def read_logs(path):
    with open(path, 'r', errors='replace') as fp:
        lines = fp.readlines()
    parsed = [(line, REGEX.match(line.strip())) for line in lines
              if line.startswith('{address space usage')]
    for line, match in parsed:
        if not match:
            print('failed to parse:', line.strip())
    return [match.groupdict() for _, match in parsed if match]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', default='uwsgi.log')
    args = parser.parse_args()
    save_logs(read_logs(args.logfile))

if __name__ == '__main__':
    main()
