#!/bin/bash

#PBS -N noVM
#PBS -S /bin/bash
#PBS -l walltime=30:00:00
#PBS -l nodes=2:ppn=10

module load numpy/1.9.1
python /home/mj1e16/periodic/astro.13py

