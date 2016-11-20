#!/bin/bash
for i in `seq 2 6`;
do
    echo $i
    python moran.py $i
done
