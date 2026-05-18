from app.services.database import DatabaseManager
try:
    db = DatabaseManager()
    print("Database initialization successful!")
except Exception as e:
    import traceback
    traceback.print_exc()
