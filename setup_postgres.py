#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script
This script helps set up the PostgreSQL database for DevCareerCompass
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def setup_postgres_database():
    """Set up PostgreSQL database tables"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL to your PostgreSQL connection string")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        # Import and create tables
        from app import app, db, init_database
        
        with app.app_context():
            # Initialize database
            init_database()
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            
            # Check if tables exist
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result.fetchall()]
                print(f"📋 Available tables: {', '.join(tables)}")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def migrate_sqlite_to_postgres():
    """Migrate data from SQLite to PostgreSQL (if needed)"""
    
    sqlite_path = "./devcareer_compass.db"
    if not os.path.exists(sqlite_path):
        print("ℹ️  No SQLite database found to migrate")
        return True
    
    print("🔄 Migrating data from SQLite to PostgreSQL...")
    
    try:
        # Import required modules
        from app import app, db
        from src.database.models import Developer, Repository, JobPosting
        
        # Create SQLite engine
        sqlite_engine = create_engine("sqlite:///./devcareer_compass.db")
        
        # Get data from SQLite
        with app.app_context():
            # Get developers
            developers = []
            with sqlite_engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM developer"))
                for row in result.fetchall():
                    developers.append(dict(row._mapping))
            
            # Get repositories
            repositories = []
            with sqlite_engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM repository"))
                for row in result.fetchall():
                    repositories.append(dict(row._mapping))
            
            # Get job postings
            job_postings = []
            with sqlite_engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM job_posting"))
                for row in result.fetchall():
                    job_postings.append(dict(row._mapping))
            
            print(f"📊 Found {len(developers)} developers, {len(repositories)} repositories, {len(job_postings)} job postings")
            
            # Insert into PostgreSQL
            if developers:
                for dev_data in developers:
                    # Remove id to let PostgreSQL auto-generate
                    dev_data.pop('id', None)
                    developer = Developer(**dev_data)
                    db.session.add(developer)
                
                db.session.commit()
                print(f"✅ Migrated {len(developers)} developers")
            
            if repositories:
                for repo_data in repositories:
                    repo_data.pop('id', None)
                    repository = Repository(**repo_data)
                    db.session.add(repository)
                
                db.session.commit()
                print(f"✅ Migrated {len(repositories)} repositories")
            
            if job_postings:
                for job_data in job_postings:
                    job_data.pop('id', None)
                    job_posting = JobPosting(**job_data)
                    db.session.add(job_posting)
                
                db.session.commit()
                print(f"✅ Migrated {len(job_postings)} job postings")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DevCareerCompass PostgreSQL Setup")
    print("=" * 40)
    
    # Check if DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set!")
        print("\nTo set up PostgreSQL:")
        print("1. Create a PostgreSQL database on Render")
        print("2. Set DATABASE_URL environment variable")
        print("3. Run this script again")
        sys.exit(1)
    
    # Setup database
    if setup_postgres_database():
        print("\n✅ Database setup completed!")
        
        # Try to migrate data
        migrate_sqlite_to_postgres()
        
        print("\n🎉 Setup complete! Your application should now work with PostgreSQL.")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
