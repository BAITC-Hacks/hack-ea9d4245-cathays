# Voice Router

## Run

1. Create a Python 3.12 virtual environment and install `backend` dependencies: `python -m pip install -e backend`.
2. Copy `backend/.env.example` to `backend/.env`; configure a provider endpoint if needed.
3. Run `uvicorn app.main:app --app-dir backend --reload`.
4. Run `npm install --prefix apps/web` then `npm run dev --prefix apps/web`.

Run `python backend/run_evaluation.py` to create predictions and invoke the checked-in evaluator. The checked-in dataset is authoritative.
Hackathon team repository for Cathays
