import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def get_connection():
    # Get the URL from the environment
    db_url = os.getenv("DB_URL")

    if not db_url:
        print("❌ Error: DB_URL not found.")
        print("Did you create the .env file?")
        return None

    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return None

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Successfully connected to Neon DB!")
        conn.close()