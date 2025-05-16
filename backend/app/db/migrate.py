import sqlite3
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Run migrations"""
    logger.info("Running database migrations...")
    
    # Get database file path
    db_path = Path(__file__).parent.parent.parent / "app.db"
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if category column exists in emails table
        cursor.execute("PRAGMA table_info(emails)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add category column if it doesn't exist
        if "category" not in column_names:
            logger.info("Adding category column to emails table...")
            cursor.execute("ALTER TABLE emails ADD COLUMN category TEXT DEFAULT 'inbox'")
            conn.commit()
            logger.info("Added category column to emails table")
            
            # Create index on category column
            cursor.execute("CREATE INDEX idx_emails_category ON emails(category)")
            conn.commit()
            logger.info("Created index on category column")
        else:
            logger.info("Category column already exists in emails table")
        
        conn.close()
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")

if __name__ == "__main__":
    migrate() 