# Voice Router

## Run

1. Create a Python 3.12 virtual environment and install `backend` dependencies: `python -m pip install -e backend`.
2. Copy `backend/.env.example` to `backend/.env`; configure a provider endpoint if needed.
3. Run `uvicorn app.main:app --app-dir backend --reload`.
4. Run `npm install --prefix apps/web` then `npm run dev --prefix apps/web`.

The web app is a responsive routing studio built with Tailwind CSS and shadcn/ui. Its development server proxies `/api` to `http://127.0.0.1:8000`. Restart Vite after changing its configuration. For production, serve `/api` through your backend reverse proxy, or set `VITE_API_URL` when building and configure that backend to allow the frontend origin.

Use **Load an example** to explore the UI without calling a provider. Live conversations show routing decisions, extracted details, execution status, and JSON traces. Session history lasts for the current browser tab; use **Export session** to save a conversation before reloading. Voice input is not configured; the studio supports text input.

Frontend checks: `npm run build --prefix apps/web` and `npm test --prefix apps/web`.

Run `$env:PYTHONIOENCODING='utf-8'; python backend/run_evaluation.py` in PowerShell to create predictions and invoke the checked-in evaluator. The checked-in dataset is authoritative.
Hackathon team repository for Cathays
