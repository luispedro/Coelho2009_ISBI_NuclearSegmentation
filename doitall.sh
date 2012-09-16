#!/usr/bin/env bash

python testenv.py || exit 1

export BASE=$PWD
[ -d my_env ] || virtualenv --system-site-packages my_env
source ./my_env/bin/activate
pip install jug
pip install mahotas
pip install imread
pip install pyslic

cd $BASE/libs/readmagick
python setup.py install

cd $BASE/sources
jug execute
python printresults.py
