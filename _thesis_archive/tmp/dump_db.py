import sqlite3
import json

def dump_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    data = {}
    
    for table in tables:
        # Get schema
        cursor.execute(f"PRAGMA table_info({table});")
        schema[table] = cursor.fetchall()
        
        # Get data sample (first 5 rows)
        cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
        data[table] = cursor.fetchall()
        
    conn.close()
    return {"schema": schema, "data": data}

if __name__ == "__main__":
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else 'traffic.db'
    res = dump_schema(db)
    print(json.dumps(res, indent=2, ensure_ascii=False))
