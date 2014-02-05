#!/bin/bash
grep -il 'LinkedIn is momentarily unavailable but should return in a few moments' html_data/* > remove.tmp

for i in $(cat remove.dat)
do
    file=$i
    echo $file
    rm $file
done
