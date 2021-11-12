#!/bin/bash
home_dir=${HOME}
virtual_environment=$home_dir"/nous_growbox/env"

if [ -d $virtual_environment ]; then
   echo "virtual environment already exists.. sourcing..."
   source env/bin/activate
else
   echo "virtual environment does not exist. creating..."
   python3.9 -m venv env
   source env/bin/activate
   pip install -r dev_requirements.txt
fi
