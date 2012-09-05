from datetime import datetime
import os
import re
from shlex import split
from subprocess import check_output, CalledProcessError, STDOUT

os.environ["SGE_ROOT"] = "/sge/GE"

def collect_status_info(context):
    try:
        result = str(check_output(split("qstat -j earwigbot"), stderr=STDOUT))
    except CalledProcessError:
        return ["offline", None, None, None]

    if result.startswith("Following jobs do not exist:"):
        return ["offline", None, None, None]

    lines = result.splitlines()[1:]
    data = {}
    for line in lines:
        re_key = re.match(r"(.*?):\s", line)
        re_val = re.search(r":\s*(.*?)$", line)
        if re_key and re_val:
            data[re_key.group(1)] = re_val
    since, uptime = _format_date(data["submission_time"])
    host = data["sge_o_host"]
    return ["online", since, uptime, host]

def _format_date(time):
    start = datetime.strptime(time, "%a %b %d %H:%M:%S %Y")
    since = start.strftime("%b %d, %Y %H:%M:%S UTC")
    diff = (datetime.utcnow() - start)
    if diff.days:
        uptime = "{0} days".format(diff.days)
        if diff.seconds >= 3600:
            uptime += ", {0} hours".format(diff.seconds / 3600)
    else:
        if diff.seconds > 3600:
            uptime = "{0} hours".format(diff.seconds / 3600)
        elif diff.seconds > 60:
            uptime = "{0} minutes".format(diff.seconds / 60)
        else:
            uptime = "{0} seconds".format(diff.seconds)
    return (since, uptime)
