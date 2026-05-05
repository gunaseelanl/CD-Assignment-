#!/usr/bin/env sh
# MD INDUSTRIES
# Developer: M.DHANESVARAN

set -eu

sh scripts/build_portable.sh
python scripts/test_portable.py
