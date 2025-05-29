from app import create_app, db, migrate

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
