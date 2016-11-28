#!/bin/bash
for i in `seq 2 5`;
do
    echo $i
    python moran.py $i
done
