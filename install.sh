#!/usr/bin/env bash

#1. verify we have SQLite
#this is for mac os
SQLITE=sqlite3
SQLITE_CHECK=$(which $SQLITE)
if [[ $SQLITE_CHECK == "sqlite not found" ]]; then
  brew install $SQLITE
fi

#2. verify if we have venv environment
if [ ! -d venv ]; then
  echo "Creating venv"
  python3 -m venv venv
fi
source venv/bin/activate

#3. export PYTHONPATH
if [[ ! $PYTHONPATH =~ $PWD ]]; then
  echo "Exporting PYTHONPATH"
  export PYTHONPATH=$PWD:$PYTHONPATH
fi

#4. install packages
pip install --upgrade pip
pip install pipenv
pip install -r requirements.txt
