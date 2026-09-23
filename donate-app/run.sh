#!/bin/sh
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -q -r requirements.txt
exec uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
