#!/bin/bash

#PBS -N noVM_baseline1304_15
#PBS -S /bin/bash
#PBS -l walltime=15:00:00
#PBS -l nodes=1:ppn=16

module load numpy/1.9.1
python /home/mj1e16/periodic/baseline1304_15.py

