#!/bin/bash

#PBS -N noVM_astro169_19
#PBS -S /bin/bash
#PBS -l walltime=15:00:00
#PBS -l nodes=1:ppn=16

module load numpy/1.9.1
python /home/mj1e16/periodic/astro169_19.py

