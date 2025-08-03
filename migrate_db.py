"""
Database migration script to add new user profile fields
Run this script to update your existing database with new columns
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_database():
    engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./test.db"))
    
    with engine.connect() as connection:
        try:
            # Add new columns to users table
            migration_queries = [
                "ALTER TABLE users ADD COLUMN first_name VARCHAR;",
                "ALTER TABLE users ADD COLUMN last_name VARCHAR;",
                "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;",
                "ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;"
            ]
            
            for query in migration_queries:
                try:
                    connection.execute(text(query))
                    print(f"✅ Executed: {query}")
                except Exception as e:
                    print(f"⚠️ Query failed (might already exist): {query}")
                    print(f"   Error: {e}")
            
            connection.commit()
            print("\n🎉 Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_database()
