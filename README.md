# AI Sales Intelligence & CRM

Resume-ready full-stack starter built with FastAPI, SQLite, SQLAlchemy, scikit-learn and React/Vite.

## Structure
- `backend/` FastAPI API, authentication, CRM models, lead scoring, analytics, copilot and ML training script.
- `frontend/` React/Vite dashboard with login, KPIs, lead prioritization and AI Copilot.

## Backend
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```
Swagger: http://127.0.0.1:8000/docs

## Frontend
Open a second terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open the Vite URL shown in the terminal.

## Demo login
Email: `admin@crm.local`
Password: `Admin@123`

## ML
After backend dependencies are installed:
```powershell
python -m app.ml.train_model
```
This trains a reproducible Random Forest conversion model on synthetic demonstration data. For a real portfolio project, replace the synthetic training data with anonymized historical CRM outcomes.
