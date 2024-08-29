#! /usr/bin/env python

import os
import subprocess


def process(*args):
    print(*args)
    subprocess.run(args, check=True)


def main():
    root = os.path.join(os.path.dirname(__file__), "static")
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            name = os.path.relpath(os.path.join(dirpath, filename))
            if filename.endswith(".js") and ".min." not in filename:
                process(
                    "uglifyjs",
                    "--compress",
                    "-o",
                    name.replace(".js", ".min.js"),
                    "--",
                    name,
                )
            if filename.endswith(".css") and ".min." not in filename:
                process(
                    "postcss",
                    "-u",
                    "cssnano",
                    "--no-map",
                    name,
                    "-o",
                    name.replace(".css", ".min.css"),
                )


if __name__ == "__main__":
    main()
