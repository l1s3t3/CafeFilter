import sqlite3
import csv

db = "KOHVIKUD.db"

def opendb():
    """
    Open SQLite database.
    """
    conn = sqlite3.connect(db)
    c = conn.cursor()
    print("Opened database successfully")
    return conn, c

def create_table():
    """
    Create table SOOKLA.
    """
    conn, c = opendb()
    c.execute("""
        CREATE TABLE SOOKLA (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(20) NOT NULL,
            location VARCHAR(20) NOT NULL,
            service_provider VARCHAR(20) NOT NULL,
            time_open VARCHAR(20) NOT NULL,
            time_closed VARCHAR(20) NOT NULL
        );
    """)
    conn.commit()
    conn.close()
    print("Table created successfully")

def import_csv_to_db(csv_file_path):
    """
    Import data from CSV file.
    """
    conn, c = opendb()

    with open(csv_file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            name = row[0]
            location = row[1]
            service_provider = row[2]
            time_open = row[3]
            time_closed = row[4]

            c.execute("""
                INSERT INTO SOOKLA (NAME, LOCATION, SERVICE_PROVIDER, TIME_OPEN, TIME_CLOSED)
                VALUES (?, ?, ?, ?, ?)
            """, (name, location, service_provider, time_open, time_closed))

    conn.commit()
    conn.close()
    print("CSV data imported successfully")

if __name__ == "__main__":
    csv_path = "kohvikud.csv"
    create_table()
    import_csv_to_db(csv_path)
