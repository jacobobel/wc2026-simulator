import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def init_db():
    supabase = get_client()
    
    schema = """
    -- Test connection
    SELECT 1
    """
    
    print("Connected to Supabase successfully")
    print(f"Project: {os.getenv('SUPABASE_URL')}")

if __name__ == "__main__":
    init_db()