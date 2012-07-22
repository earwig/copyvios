#! /usr/bin/env python
# -*- coding: utf-8  -*-

import logging
import os
import shutil

page_src = """#! /usr/bin/env python
# -*- coding: utf-8  -*-
import os
import sys

os.chdir("..")
sys.path.insert(0, os.path.join(".", "{{pages_dir}}"))

from mako.template import Template
from mako.lookup import TemplateLookup

def myapp(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html")])
    lookup = TemplateLookup(directories=["{{pages_dir}}"],
                            input_encoding="utf8")
    template = Template(filename="{{src}}", module_directory="{{temp_dir}}",
                        lookup=lookup, format_exceptions=True)
    return [template.render(environ=environ).encode("utf8")]

if __name__ == "__main__":
    from flup.server.fcgi import WSGIServer
    WSGIServer(myapp).run()
"""

rewrite_script_src = """match URL into $ with ^/~earwig/{0}(\?.*?)?$
if matched then
    set URL = /~earwig/rewrite/{0}.fcgi$1
    goto END
endif
"""

class Builder(object):
    def __init__(self):
        self.build_dir = "www"
        self.static_dir = "static"
        self.pages_dir = "pages"
        self.support_dir = "pages/support"
        self.temp_dir = "temp"
        self.rs_file = "rewrite.script"

        self.root = logging.getLogger("builder")
        self.root.addHandler(logging.NullHandler())
        self._pages = []

    def _enable_logging(self):
        handler = logging.StreamHandler()
        handler.setFormatter(_LogFormatter())
        self.root.addHandler(handler)
        self.root.setLevel(logging.DEBUG)

    def _gen_page(self, page, base):
        if not page.endswith(".mako"):
            base.warn("Skipping {0} (not endswith('.mako'))".format(page))
            return

        logger = base.getChild(page.rsplit(".", 1)[0])
        self._pages.append(page.rsplit(".", 1)[0])
        src = os.path.join(self.pages_dir, page)
        dest = os.path.join(self.build_dir, page.replace(".mako", ".fcgi"))

        logger.debug("build {0} -> {1}".format(src, dest))
        content = page_src.replace("{{src}}", src)
        content = content.replace("{{pages_dir}}", self.pages_dir)
        content = content.replace("{{temp_dir}}", self.temp_dir)
        with open(dest, "w") as fp:
            fp.write(content)

        logger.debug("chmod 0755 {0}".format(dest))
        os.chmod(dest, 0755)

    def clean(self):
        logger = self.root.getChild("clean")
        targets = (self.build_dir, self.temp_dir)

        for target in targets:
            if os.path.exists(target):
                logger.debug("rm -r {0}".format(target))
                shutil.rmtree(target)

            logger.debug("mkdir {0}".format(target))
            os.mkdir(target)

    def gen_static(self):
        logger = self.root.getChild("static")
        dest = os.path.join(self.build_dir, "static")

        logger.debug("copytree {0} -> {1}".format(self.static_dir, dest))
        shutil.copytree(self.static_dir, dest)

    def gen_pages(self):
        logger = self.root.getChild("pages")
        pages = os.listdir(self.pages_dir)
        for page in pages:
            if not os.path.isfile(os.path.join(self.pages_dir, page)):
                continue
            self._gen_page(page, logger)

    def gen_zws(self):
        logger = self.root.getChild("zws")
        target = self.rs_file

        if os.path.exists(target):
            logger.debug("rm {0}".format(target))
            os.remove(target)

        logger.debug("build rewrite.script")
        with open(target, "w") as fp:
            for page in self._pages:
                fp.write(rewrite_script_src.format(page))

    def build(self):
        self._enable_logging()
        self.root.info("Building project...")
        self.clean()
        self.gen_static()
        self.gen_pages()
        self.gen_zws()
        self.root.info("Done!")


class _LogFormatter(logging.Formatter):
    def __init__(self):
        fmt = "[%(asctime)s %(lvl)s] %(name)s: %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        _format = super(_LogFormatter, self).format
        self.format = lambda record: _format(self.colorize(record))
        super(_LogFormatter, self).__init__(fmt=fmt, datefmt=datefmt)

    def colorize(self, record):
        l = record.levelname.ljust(8)
        if record.levelno == logging.DEBUG:
            record.lvl = l.join(("\x1b[34m", "\x1b[0m"))  # Blue
        if record.levelno == logging.INFO:
            record.lvl = l.join(("\x1b[32m", "\x1b[0m"))  # Green
        if record.levelno == logging.WARNING:
            record.lvl = l.join(("\x1b[33m", "\x1b[0m"))  # Yellow
        if record.levelno == logging.ERROR:
            record.lvl = l.join(("\x1b[31m", "\x1b[0m"))  # Red
        if record.levelno == logging.CRITICAL:
            record.lvl = l.join(("\x1b[1m\x1b[31m", "\x1b[0m"))  # Bold red
        return record


if __name__ == "__main__":
    Builder().build()
