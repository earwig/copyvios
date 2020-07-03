import re
import sqlite3

REGEX = re.compile(
    r'^'
    r'{address space usage: (?P<used_bytes>\d+) bytes/(?P<used_mb>\w+)} '
    r'{rss usage: (?P<rss_bytes>\d+) bytes/(?P<rss_mb>\w+)} '
    r'\[pid: (?P<pid>\d+)\|app: -\|req: -/-\] (?P<ip>[0-9.]+) \(-\) '
    r'{(?P<vars>\d+) vars in (?P<var_bytes>\d+) bytes} '
    r'\[(?P<date>[0-9A-Za-z: ]+)\] (?P<method>\w+) (?P<url>.*?) => '
    r'generated (?P<resp_bytes>\d+) bytes in (?P<msecs>\d+) msecs '
    r'\((?P<proto>[A-Z0-9/.]+) (?P<status>\d+)\) '
    r'(?P<headers>\d+) headers in (?P<header_bytes>\d+) bytes '
    r'\((?P<switches>\d+) switches on core (?P<core>\d+)\) '
    r'(?P<agent>.*?)'
    r'$'
)

def save_logs(logs):
    columns = sorted(REGEX.groupindex, key=lambda col: REGEX.groupindex[col])
    conn = sqlite3.Connection('logs.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE logs(%s)' % ', '.join(columns))
    cur.executemany('INSERT INTO logs VALUES (%s)' % ', '.join(['?'] * len(columns)),
                    [[log[col] for col in columns] for log in logs])
    conn.commit()
    conn.close()

def read_logs(path):
    with open(path) as fp:
        lines = fp.readlines()
    return [REGEX.match(line.strip()).groupdict() for line in lines
            if line.startswith('{address space usage')]

if __name__ == '__main__':
    save_logs(read_logs('uwsgi.log'))
