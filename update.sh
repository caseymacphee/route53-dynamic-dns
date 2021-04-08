#! /bin/bash    

# this should be a python 3.8 virtual env
cd my/virtual/env/root/dir
source bin/activate

# virtualenv is now active, which means your PATH has been modified.
# Don't try to run python from /usr/bin/python, just run "python" and
# let the PATH figure out which version to run (based on what your
# virtualenv has configured).

python update_ddns.py