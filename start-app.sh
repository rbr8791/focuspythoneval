#!/bin/bash

source activate default37
export FLASK_APP=iap.py
export FLASK_ENV=development
export FLASK_DEBUG=1

flask run