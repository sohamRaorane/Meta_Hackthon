# Streamlit Setup Guide

This project uses a Streamlit UI in `app.py` on port `7860` and a FastAPI backend on port `7861`.

## What you need
- Python 3.11 or later
- `pip`

## Install dependencies
```bash
pip install -r requirements.txt
```

If Streamlit is not installed yet, this command will add it because it is included in `requirements.txt`.

## Run the UI
```bash
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
```

## What happens when it starts
- Streamlit launches the visual UI
- `app.py` starts the FastAPI server on port `7861` in a background thread
- The UI talks to the backend through `http://localhost:7861`

## Optional backend-only check
If you want to test the backend by itself, you can run it on `7861` without opening the UI:
```bash
py -m uvicorn server.app:app --host 0.0.0.0 --port 7861
```

Then open:
- Streamlit UI: `http://localhost:7860`
- FastAPI docs: `http://localhost:7861/docs`

## Recommended local workflow
Use the Streamlit command for normal use:
- `streamlit run app.py --server.port 7860 --server.address 0.0.0.0`

Use the backend command only when you want API docs or backend debugging:
- `py -m uvicorn server.app:app --host 0.0.0.0 --port 7861`

## If something fails
- Make sure nothing else is already using port `7860` or `7861`
- Reinstall dependencies with `pip install -r requirements.txt`
- Check that `streamlit` and `fastapi` are installed in the same Python environment
