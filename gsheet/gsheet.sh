#!/bin/bash
# /usr/local/bin/python3 --version
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/../
/usr/local/bin/python3 -m gsheet.gsheet
