#! /usr/bin/env python
# -*- coding: utf-8  -*-

import os
import subprocess

def process(program, old_file, new_file):
    print "%s: %s -> %s" % (program, old_file, new_file)
    content = subprocess.check_output([program, old_file])
    with open(new_file, "w") as fp:
        fp.write(content)

def main():
    root = os.path.join(os.path.dirname(__file__), "static")
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            name = os.path.join(dirpath, filename)
            if filename.endswith(".js") and ".min." not in filename:
                process("uglifyjs", name, name.replace(".js", ".min.js"))
            if filename.endswith(".css") and ".min." not in filename:
                process("uglifycss", name, name.replace(".css", ".min.css"))

if __name__ == "__main__":
    main()
