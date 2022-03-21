#!/bin/bash

CWD=`pwd`
filename=$1

chromium-browser --headless --no-sandbox --disable-gpu --disable-software-rasterizer --screenshot --hide-scrollbars --window-size=600,448 ./testProfileCard.html 
../image.py screenshot.png
