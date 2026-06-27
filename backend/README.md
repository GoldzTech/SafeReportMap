#Iniciar o Backend:

PYTHONPATH=. uvicorn backend.app.main:app --reload

#Entrar na db:

sudo -u postgres psql -d safereport_map