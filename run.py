# run.py

import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, seed_initial_data

app = create_app()

@app.cli.command("seed")
def seed_command():
    """Seeds the database with initial data."""
    seed_initial_data(app)

if __name__ == '__main__':
    app.run(debug=True, port=5001) # <--- Add port=5001 here