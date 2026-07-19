import os
import psycopg2

db_url = None
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('DATABASE_URL='):
            db_url = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

if not db_url:
    print("No DATABASE_URL found in .env")
    exit(1)

print("Connecting to DB...")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

try:
    cur.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'users_gender_check';")
    print("Constraint definition:", cur.fetchone())
except Exception as e:
    print("Error:", e)

try:
    cur.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_gender_check;")
    conn.commit()
    print("Dropped users_gender_check constraint successfully!")
except Exception as e:
    conn.rollback()
    print("Could not drop constraint:", e)

cur.close()
conn.close()
