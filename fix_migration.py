"""
Fixed database migration script for SQLite limitations
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def fix_migration():
    engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./test.db"))
    
    with engine.connect() as connection:
        try:
            # First, check what columns exist
            result = connection.execute(text("PRAGMA table_info(users);"))
            existing_columns = [row[1] for row in result.fetchall()]
            print(f"Existing columns: {existing_columns}")
            
            # Add created_at and updated_at columns without default constraints
            if 'created_at' not in existing_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME;"))
                print("✅ Added created_at column")
                
            if 'updated_at' not in existing_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME;"))
                print("✅ Added updated_at column")
            
            # Update existing records with current timestamp
            current_time = datetime.utcnow().isoformat()
            connection.execute(text(f"""
                UPDATE users 
                SET created_at = '{current_time}', 
                    updated_at = '{current_time}' 
                WHERE created_at IS NULL OR updated_at IS NULL
            """))
            print("✅ Updated existing records with timestamps")
            
            connection.commit()
            print("\n🎉 Database migration fixed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    fix_migration()
