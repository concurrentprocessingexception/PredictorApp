# Predictor App

Python backend for stock pricing and forecasting.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with:

```
DATABASE_URL=sqlite:///./test.db
FINNHUB_API_KEY=your_key
UPLOAD_ENABLED=false
ALLOW_ORIGINS=http://localhost:5173
```

Run alembic migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
uvicorn app.main:app --reload
```

Docs available at `http://localhost:8000/docs`.
