"""
MemeGPT — Migrate all memes and data from local SQLite to Railway PostgreSQL.
Specification: 06_Deployment_Railway_Vercel.md
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Meme, Base

def main():
    # Local SQLite
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memegpt.db")
    sqlite_url = f"sqlite:///{sqlite_path}"
    sqlite_engine = create_engine(sqlite_url)

    # Railway PostgreSQL
    postgres_url = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")
    if not postgres_url or "sqlite" in postgres_url:
        print("❌ DATABASE_URL must point to PostgreSQL for migration.")
        print(f"Current DATABASE_URL: {postgres_url}")
        return

    postgres_engine = create_engine(postgres_url)

    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(postgres_engine)

    SqliteSession = sessionmaker(bind=sqlite_engine)
    PgSession = sessionmaker(bind=postgres_engine)

    sqlite_db = SqliteSession()
    pg_db = PgSession()

    try:
        memes = sqlite_db.query(Meme).all()
        print(f"Copying {len(memes)} memes to PostgreSQL...")

        for idx, meme in enumerate(memes, 1):
            pg_db.merge(meme)
            if idx % 100 == 0:
                pg_db.commit()
                print(f"  Migrated {idx}/{len(memes)}...")

        pg_db.commit()
        print("✅ Migration complete!")
    except Exception as e:
        pg_db.rollback()
        print(f"❌ Migration error: {e}")
    finally:
        sqlite_db.close()
        pg_db.close()


if __name__ == "__main__":
    main()
