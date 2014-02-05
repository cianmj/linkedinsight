#!/bin/bash
grep -il 'You and this LinkedIn user don’t know anyone in common.' html_data/* > blacklist.tmp

sed 's/html_data\///g' blacklist.tmp > tmp.txt
sed 's/.html//g' tmp.txt > blacklist.dat

rm -rf blacklist.tmp tmp.txt



