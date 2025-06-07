# run.py (Tidak ada perubahan yang diperlukan, hanya konfirmasi port 5001)

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
    # Pastikan hanya satu baris app.run() yang aktif
    app.run(debug=True, host='0.0.0.0', port=5001)