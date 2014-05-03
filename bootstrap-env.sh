#!/usr/bin/env sh

virtualenv2 .venv
source .venv/bin/activate
pip install -r requirements.txt

ln -s create .venv/lib/python2.7/site-packages/

echo "Run: source .venv/bin/activate"
echo "then python -m create"

