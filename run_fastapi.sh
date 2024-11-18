#!/bin/sh

cd "$(dirname "$0")"

python3 main.py

if [ ! -d .venv ]; then
	python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r requirements_fastapi.txt
uvicorn data.fastapi.main:app --reload
