#!/bin/bash
# here we are going to do the cluster thing
# ./wcluster --text "" --c ""
list=''
for cluster in "$@"
do
    ./wcluster --text input.txt --c $cluster
    list="${list} ${cluster}"
done
#python3 cleanInput.py "$list"
