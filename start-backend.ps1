# Start the FastAPI backend (requires PostgreSQL — run: docker compose up -d)
Set-Location $PSScriptRoot\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
