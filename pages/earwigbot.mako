<%!
    from datetime import datetime
    import os
    import re
    from shlex import split
    from subprocess import check_output, CalledProcessError, STDOUT

    os.environ["SGE_ROOT"] = "/sge62"

    def format_date(d):
        start = datetime.strptime(d, "%a %b %d %H:%M:%S %Y")
        since = start.strftime("%b %d, %Y at %H:%M:%S UTC")
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

    def collect_status_info():
        try:
            result = check_output(["qstat", "-j", "earwigbot"], stderr=STDOUT)
        except CalledProcessError as e:
            return ["offline"]

        if result.startswith("Following jobs do not exist:"):
            return ["offline"]

        lines = result.splitlines()[1:]
        re_key = "^(.*?):\s"
        re_val = ":\s*(.*?)$"
        data = dict((re.search(re_key, line).group(1), re.search(re_val, line).group(1)) for line in lines)
        since, uptime = format_date(data["submission_time"])
        host = data["sge_o_host"]
        return ["online", since, uptime, host]
%>\
<%def name="get_status()" filter="trim">
    <% status, since, uptime, host = collect_status_info() %>
    <span class="${status}">${status}</span>
    % if status == "online":
        since ${since} (${uptime} uptime) on <tt>${host}</tt>
    % endif
</%def>\
<%include file="/support/header.mako" args="environ=environ, title='EarwigBot Status'"/>
            <h1>EarwigBot Status</h1>
            <p>EarwigBot is ${get_status()}.</p>
            <p>Additional information: <a href="http://status.toolserver.org/">status.toolserver.org</a></p>
<%include file="/support/footer.mako" args="environ=environ"/>
