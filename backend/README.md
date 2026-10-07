# AI Sales Intelligence & CRM - Backend

FastAPI + SQLite + SQLAlchemy + scikit-learn.

## Run

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

Default admin: `admin@crm.local` / `Admin@123`

For the demo frontend, use the same API. The current starter implements authentication, customers, leads, deals, activities, dashboard metrics and a deterministic sales copilot. The ML training script generates a reproducible synthetic training set and saves a Random Forest model.
