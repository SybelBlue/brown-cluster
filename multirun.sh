#!/bin/bash
# here we are going to do the cluster thing
# ./wcluster --text "" --c ""
list=''
for cluster in "$@"
do
    ./wcluster --text cleaned-lolcat.txt --c $cluster
    list="${list},${cluster}"
done
python3 multiTree.py --clusters "[${list:1}]" cleaned-lolcat
