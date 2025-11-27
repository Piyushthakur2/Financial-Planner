# AI Personal Finance Advisor

Full project scaffold (FastAPI backend + Gemini + React frontend). See backend/ and frontend/ for code.

Run locally:

1. Set GEMINI_API_KEY in backend/.env or environment.

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm start
```

To deploy: use the provided Dockerfile at repository root. Set GEMINI_API_KEY in your host (Render/other platform).
