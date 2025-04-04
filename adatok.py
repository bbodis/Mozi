import sqlite3

def print_table(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    print(f"\n=== {table_name.upper()} ===")
    print(" | ".join(columns))
    print("-" * 50)
    for row in rows:
        print(" | ".join(str(item) for item in row))
    print("-" * 50 + "\n")
def main():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    for table_name in tables:
        print_table(cursor, table_name)
    conn.close()
if __name__ == "__main__":
    main()
