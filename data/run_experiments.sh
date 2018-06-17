#!/bin/bash

for i in 10 12;
do
    ./run_experiment.py ${i} output/out${i}.txt
done



