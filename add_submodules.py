import sys
import re
import os

repodir = os.getcwd()
with open(sys.argv[1]) as modulefile:
    for line in modulefile:
        if (match := re.search(r'path = (.+)', line)):
            path = match.group(1)
        if (match := re.search(r'url = (.+)', line)):
            url = match.group(1)

            basedir = os.path.dirname(path)
            os.makedirs(basedir, exist_ok=True)
            print(f'chdir {basedir}')
            os.chdir(basedir)
            command_to_run = f"git submodule add {url}"
            print(command_to_run)
            os.system(command_to_run)
            os.chdir(repodir)
