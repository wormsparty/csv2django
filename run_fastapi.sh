#!/bin/sh

cd "$(dirname "$0")"

python3 csv2fastapi.py
python3 csv2test.py

if [ ! -d .venv ]; then
	python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r output/fastapi/requirements.txt
uvicorn output.fastapi.main:app --reload
