"""
MemeGPT — Migrate all models and tables from local SQLite to PostgreSQL (Supabase/Railway).
Specification: 06_Database/Database_Overview.md & 06_Deployment_Railway_Vercel.md
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import (
    Base,
    User,
    Meme,
    ApiKey,
    DeviceToken,
    SavedMeme,
    MemeVote,
    MemeUsage,
    FavouriteMeme,
    MemeFlag,
    Feedback,
    SearchLog,
)

TABLE_MODELS = [
    User,
    Meme,
    ApiKey,
    DeviceToken,
    SavedMeme,
    MemeVote,
    MemeUsage,
    FavouriteMeme,
    MemeFlag,
    Feedback,
    SearchLog,
]


def main():
    # Local SQLite
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memegpt.db")
    sqlite_url = f"sqlite:///{sqlite_path}"
    sqlite_engine = create_engine(sqlite_url)

    # PostgreSQL (Supabase / Railway)
    postgres_url = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")
    if not postgres_url or "sqlite" in postgres_url:
        print("❌ DATABASE_URL must point to PostgreSQL for migration.")
        print(f"Current DATABASE_URL: {postgres_url}")
        return

    postgres_engine = create_engine(postgres_url)

    print("Creating all tables in PostgreSQL if not already present...")
    Base.metadata.create_all(postgres_engine)

    print("Applying PostgreSQL production indexes (GIN, composite B-tree)...")
    from app.services.database_service import generate_postgres_index_ddl
    ddl_statements = generate_postgres_index_ddl()
    with postgres_engine.connect() as pg_conn:
        for stmt in ddl_statements.split(";"):
            cleaned = stmt.strip()
            if cleaned and not cleaned.startswith("--"):
                try:
                    pg_conn.exec_driver_sql(cleaned)
                except Exception as ex:
                    print(f"  Notice applying index '{cleaned[:40]}...': {ex}")

    SqliteSession = sessionmaker(bind=sqlite_engine)
    PgSession = sessionmaker(bind=postgres_engine)

    sqlite_db = SqliteSession()
    pg_db = PgSession()

    try:
        for model in TABLE_MODELS:
            table_name = model.__tablename__
            rows = sqlite_db.query(model).all()
            print(f"Migrating table '{table_name}': {len(rows)} records found...")
            cols = [c.name for c in model.__table__.columns]
            for idx, item in enumerate(rows, 1):
                data = {col: getattr(item, col) for col in cols}
                pg_db.merge(model(**data))
                if idx % 100 == 0:
                    pg_db.commit()
            pg_db.commit()
            print(f"  ✓ Table '{table_name}' migrated ({len(rows)} rows).")

        print("✅ Full SQLite to PostgreSQL migration completed successfully!")
    except Exception as e:
        pg_db.rollback()
        print(f"❌ Migration error: {e}")
    finally:
        sqlite_db.close()
        pg_db.close()


if __name__ == "__main__":
    main()
