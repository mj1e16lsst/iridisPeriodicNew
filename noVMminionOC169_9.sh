#!/bin/bash

#PBS -N noVM_minionOC169_9
#PBS -S /bin/bash
#PBS -l walltime=15:00:00
#PBS -l nodes=1:ppn=16

module load numpy/1.9.1
python /home/mj1e16/periodic/minionOC169_9.py

