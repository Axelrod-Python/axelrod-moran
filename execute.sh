#!/bin/bash
for i in `seq 2 12`;
do
    echo $i
    python moran.py $i
done
