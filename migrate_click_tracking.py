"""
Database migration to add click tracking fields to existing short_links table
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_click_tracking():
    """Add click tracking columns to existing short_links table"""
    engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./test.db"))
    
    with engine.connect() as connection:
        try:
            # Add click tracking columns to short_links table
            migration_queries = [
                "ALTER TABLE short_links ADD COLUMN click_count INTEGER DEFAULT 0;",
                "ALTER TABLE short_links ADD COLUMN last_clicked DATETIME;",
                "ALTER TABLE short_links ADD COLUMN created_at DATETIME;",
                "ALTER TABLE short_links ADD COLUMN updated_at DATETIME;",
            ]
            
            for query in migration_queries:
                try:
                    connection.execute(text(query))
                    print(f"✅ Added column: {query.split('ADD COLUMN')[1].split()[0]}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️ Column already exists: {query.split('ADD COLUMN')[1].split()[0]}")
                    else:
                        print(f"❌ Failed to add column: {e}")
            
            # Update existing records with default values
            update_queries = [
                "UPDATE short_links SET click_count = 0 WHERE click_count IS NULL;",
                "UPDATE short_links SET created_at = datetime('now') WHERE created_at IS NULL;",
                "UPDATE short_links SET updated_at = datetime('now') WHERE updated_at IS NULL;"
            ]
            
            for query in update_queries:
                try:
                    result = connection.execute(text(query))
                    print(f"✅ Updated {result.rowcount} existing records")
                except Exception as e:
                    print(f"❌ Failed to update records: {e}")
            
            connection.commit()
            print("\n🎉 Click tracking migration completed successfully!")
            print("\n📊 New features available:")
            print("   - Click count for each link")
            print("   - Last clicked timestamp")
            print("   - Creation and update timestamps")
            print("   - Analytics in /links/my-links endpoint")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            connection.rollback()

if __name__ == "__main__":
    migrate_click_tracking()
