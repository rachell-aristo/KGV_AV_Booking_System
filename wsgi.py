#entrypoint for Vercel (it looks for an `app` in wsgi.py) - run.py is still used for running locally
from app.main.app import app
