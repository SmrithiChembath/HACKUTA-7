Run locally:

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)/../..
uvicorn apps.api.main:app --reload --port 8000
```
