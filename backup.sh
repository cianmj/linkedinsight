#!/bin/bash

tar -cvf "$(date +%y_%m_%d-%s).tar" *.py *.p *.html *.dat user_data static templates

rsync -auvz *.* /Users/cianmj/Google\ Drive/code/skillify

