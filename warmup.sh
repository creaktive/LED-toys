#!/bin/bash
dirname=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
env="$dirname/.env"
echo PLASMA_WARMUP=$* > $env
sudo service plasma start
sleep 5
echo PLASMA_WARMUP=10 > $env
