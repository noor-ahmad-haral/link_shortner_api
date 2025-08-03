"""
Database migration to add advanced analytics tables and fields
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_analytics():
    """Add advanced analytics tables and fields"""
    engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./test.db"))
    
    with engine.connect() as connection:
        try:
            print("🚀 Starting advanced analytics migration...")
            
            # Add unique_clicks column to short_links table
            analytics_columns = [
                "ALTER TABLE short_links ADD COLUMN unique_clicks INTEGER DEFAULT 0;",
            ]
            
            for query in analytics_columns:
                try:
                    connection.execute(text(query))
                    print(f"✅ Added column: {query.split('ADD COLUMN')[1].split()[0]}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"⚠️ Column already exists: {query.split('ADD COLUMN')[1].split()[0]}")
                    else:
                        print(f"❌ Failed to add column: {e}")
            
            # Create link_clicks table for detailed analytics
            create_clicks_table = """
            CREATE TABLE IF NOT EXISTS link_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id INTEGER NOT NULL,
                
                -- Network information
                ip_address VARCHAR(45),
                user_agent TEXT,
                referer VARCHAR(500),
                
                -- Geographic data
                country VARCHAR(100),
                country_code VARCHAR(2),
                city VARCHAR(100),
                region VARCHAR(100),
                latitude REAL,
                longitude REAL,
                timezone VARCHAR(50),
                isp VARCHAR(200),
                
                -- Browser information
                browser_name VARCHAR(100),
                browser_version VARCHAR(50),
                browser_family VARCHAR(50),
                
                -- Operating System information
                os_name VARCHAR(100),
                os_version VARCHAR(50),
                os_family VARCHAR(50),
                
                -- Device information
                device_type VARCHAR(50),
                device_brand VARCHAR(100),
                device_model VARCHAR(100),
                device_family VARCHAR(100),
                
                -- Screen and technical details
                screen_resolution VARCHAR(20),
                color_depth INTEGER,
                pixel_ratio REAL,
                
                -- Behavioral tracking
                is_unique BOOLEAN DEFAULT 0,
                is_bot BOOLEAN DEFAULT 0,
                session_id VARCHAR(100),
                
                -- Timestamps
                clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed_at DATETIME,
                
                FOREIGN KEY (link_id) REFERENCES short_links (id) ON DELETE CASCADE
            );
            """
            
            try:
                connection.execute(text(create_clicks_table))
                print("✅ Created link_clicks table for detailed analytics")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("⚠️ link_clicks table already exists")
                else:
                    print(f"❌ Failed to create link_clicks table: {e}")
            
            # Create indexes for better performance
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_link_clicks_link_id ON link_clicks(link_id);",
                "CREATE INDEX IF NOT EXISTS idx_link_clicks_clicked_at ON link_clicks(clicked_at);",
                "CREATE INDEX IF NOT EXISTS idx_link_clicks_country ON link_clicks(country);",
                "CREATE INDEX IF NOT EXISTS idx_link_clicks_device_type ON link_clicks(device_type);",
                "CREATE INDEX IF NOT EXISTS idx_link_clicks_browser_name ON link_clicks(browser_name);",
                "CREATE INDEX IF NOT EXISTS idx_link_clicks_os_name ON link_clicks(os_name);",
                "CREATE INDEX IF NOT EXISTS idx_link_clicks_is_unique ON link_clicks(is_unique);",
                "CREATE INDEX IF NOT EXISTS idx_link_clicks_session_id ON link_clicks(session_id);",
                "CREATE INDEX IF NOT EXISTS idx_short_links_user_clicks ON short_links(user_id, click_count);",
                "CREATE INDEX IF NOT EXISTS idx_short_links_unique_clicks ON short_links(unique_clicks);"
            ]
            
            for query in index_queries:
                try:
                    connection.execute(text(query))
                    table_name = query.split('ON ')[1].split('(')[0] if 'ON ' in query else 'unknown'
                    print(f"✅ Created index on {table_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        pass  # Index already exists, that's fine
                    else:
                        print(f"⚠️ Index creation warning: {e}")
            
            # Update existing records with default values
            update_queries = [
                "UPDATE short_links SET unique_clicks = 0 WHERE unique_clicks IS NULL;",
            ]
            
            for query in update_queries:
                try:
                    result = connection.execute(text(query))
                    print(f"✅ Updated {result.rowcount} existing records with unique_clicks = 0")
                except Exception as e:
                    print(f"❌ Failed to update existing records: {e}")
            
            connection.commit()
            print("\n🎉 Advanced analytics migration completed successfully!")
            print("\n📊 New analytics features available:")
            print("   📈 Detailed click tracking with device/browser/location data")
            print("   🌍 Geographic analytics (country, city, timezone)")
            print("   📱 Device analytics (mobile/desktop, brands, models)")
            print("   🌐 Browser and OS analytics")
            print("   👥 Unique visitor tracking")
            print("   🕐 Time-based analytics")
            print("   📤 Export functionality (JSON/CSV)")
            print("   📊 Analytics dashboard")
            print("\n🔗 New API endpoints:")
            print("   GET /analytics/{link_id}/overview")
            print("   GET /analytics/{link_id}/devices")
            print("   GET /analytics/{link_id}/geography")
            print("   GET /analytics/{link_id}/timeline")
            print("   GET /analytics/{link_id}/export")
            print("   GET /analytics/dashboard")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            connection.rollback()

if __name__ == "__main__":
    migrate_analytics()
