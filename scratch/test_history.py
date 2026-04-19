import sqlite3
import time
import os
import sys

# Add backend/app to path
sys.path.append(os.path.abspath("backend"))

from app.db.database import get_conn
from app.db.repository import get_history
from app.config import settings

def test():
    conn = get_conn(settings.db_path)
    try:
        print(f"Testing get_history for 12 hours (720 min)...")
        data = get_history(conn, 720, "minute")
        print(f"Got {len(data)} items")
        if data:
            print(f"Sample: {data[0]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test()
