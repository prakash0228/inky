#!/bin/bash

CWD=`pwd`
filename=$1

chromium-browser --headless --screenshot --window-size=600,448 file://$CWD/$filename
../image.py screenshot.png
