#!/usr/bin/env python3
"""
migrate_sqlite_to_mysql.py — Migrate all data from SQLite to MySQL.

Usage:
    # 1. Set DATABASE_URL to your MySQL connection
    export DATABASE_URL=mysql+pymysql://root:password@localhost/skillbridge?charset=utf8mb4

    # 2. Ensure your SQLite DB exists (default: instance/skillbridge.db)
    #    Override with: export SKILLBRIDGE_SQLITE_PATH=/path/to/skillbridge.db

    # 3. Run the migration
    python migrate_sqlite_to_mysql.py

What it does:
    - Reads the existing SQLite database
    - Connects to the target MySQL database
    - Creates all tables in MySQL (via SQLAlchemy model metadata)
    - Transfers all records preserving IDs, timestamps, and foreign keys
    - Validates row counts for each table
"""
import os
import sys
from datetime import datetime

# ── Ensure project root is on sys.path ─────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.pool import NullPool

# ── Configuration ──────────────────────────────────────────────────────────

INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")
SQLITE_PATH = os.environ.get(
    "SKILLBRIDGE_SQLITE_PATH",
    os.path.join(INSTANCE_DIR, "skillbridge.db"),
)

MYSQL_URL = os.environ.get("DATABASE_URL")
if not MYSQL_URL:
    print("ERROR: DATABASE_URL environment variable is not set.")
    print("Usage: export DATABASE_URL=mysql+pymysql://root:password@localhost/skillbridge")
    sys.exit(1)

# ── Table dependency order (parents first to respect FK constraints) ──────
TABLE_ORDER = [
    "users",
    "courses",
    "badges",
    "user_profiles",
    "enrollments",
    "completed_modules",
    "certificates",
    "quizzes",
    "quiz_questions",
    "quiz_attempts",
    "course_notes_files",
    "skill_path_enrollments",
    "user_badges",
    "mentor_profiles",
    "mentor_ratings",
    "doubt_requests",
    "path_step_progress",
    "learning_analytics",
    "chat_messages",
    "job_postings",
]


def log(msg: str):
    print(f"[{datetime.now():%H:%M:%S}] {msg}")


def get_sqlite_engine():
    if not os.path.exists(SQLITE_PATH):
        log(f"ERROR: SQLite database not found at {SQLITE_PATH}")
        sys.exit(1)
    log(f"Connecting to SQLite: {SQLITE_PATH}")
    return create_engine(f"sqlite:///{SQLITE_PATH}", poolclass=NullPool)


def get_mysql_engine():
    log(f"Connecting to MySQL: {MYSQL_URL}")
    return create_engine(MYSQL_URL, poolclass=NullPool)


def reflect_tables_from_engine(engine, meta: MetaData):
    """Reflect all table schemas from engine into meta."""
    inspector = inspect(engine)
    for tname in inspector.get_table_names():
        meta.reflect(engine, only=[tname], extend_existing=True, resolve_fks=False)


def get_model_tables() -> MetaData:
    """Import all SQLAlchemy models and return their metadata."""
    log("Importing Flask/SQLAlchemy models to get table definitions...")
    os.environ["DATABASE_URL"] = MYSQL_URL
    from skillbridge.extensions import db
    from skillbridge import models  # noqa: F401 — registers models with db
    return db.metadata


def create_tables_in_mysql(mysql_engine, metadata: MetaData):
    """Create all model tables in MySQL."""
    existing = inspect(mysql_engine).get_table_names()
    to_create = [t for t in metadata.tables if t not in existing]
    if not to_create:
        log("All tables already exist in MySQL.")
        return
    log(f"Creating tables in MySQL: {to_create}")
    metadata.create_all(mysql_engine)
    log("Tables created successfully.")


def copy_table(
    sqlite_conn,
    mysql_conn,
    metadata: MetaData,
    tname: str,
    batch_size: int = 500,
):
    """Copy all rows from SQLite table to MySQL table."""
    if tname not in metadata.tables:
        log(f"  SKIP: table '{tname}' not found in model metadata")
        return 0

    table = metadata.tables[tname]

    # Read rows from SQLite (handle quoted table names)
    sqlite_rows = sqlite_conn.execute(
        text(f"SELECT * FROM [{tname}]")
    ).fetchall()
    if not sqlite_rows:
        log(f"  {tname}: 0 rows (empty)")
        return 0

    columns = [col.name for col in table.columns]
    total = len(sqlite_rows)
    inserted = 0

    # Get primary key column info
    pk_columns = [col for col in table.columns if col.primary_key]

    for i in range(0, total, batch_size):
        batch = sqlite_rows[i: i + batch_size]
        batch_dicts = []
        for row in batch:
            row_dict = dict(zip(columns, row))
            # Type conversions for MySQL compatibility
            for col_name in columns:
                val = row_dict[col_name]
                if isinstance(val, datetime):
                    pass  # MySQL DATETIME accepts datetime objects
                elif isinstance(val, bool):
                    row_dict[col_name] = int(val)
                elif val is None:
                    pass
            batch_dicts.append(row_dict)

        # Build INSERT … ON DUPLICATE KEY UPDATE to handle existing rows
        for row_dict in batch_dicts:
            stmt = table.insert().values(**row_dict)
            try:
                mysql_conn.execute(stmt)
            except Exception as exc:
                log(f"  ERROR inserting into {tname}: {exc}")
                log(f"  Row data: {row_dict}")
                raise
        mysql_conn.commit()

        inserted += len(batch)
        log(f"  {tname}: {inserted}/{total} rows")

    log(f"  {tname}: completed ({total} rows)")
    return total


def validate_counts(sqlite_engine, mysql_engine, metadata: MetaData):
    """Compare row counts between SQLite and MySQL."""
    log("\n── Validating row counts ──")
    all_ok = True
    with sqlite_engine.connect() as s_conn:
        with mysql_engine.connect() as m_conn:
            for tname in sorted(metadata.tables.keys()):
                sqlite_count = 0
                mysql_count = 0
                try:
                    sqlite_count = s_conn.execute(
                        text(f"SELECT COUNT(*) FROM [{tname}]")
                    ).scalar()
                except Exception:
                    pass
                try:
                    mysql_count = m_conn.execute(
                        text(f"SELECT COUNT(*) FROM `{tname}`")
                    ).scalar()
                except Exception:
                    pass
                status = "✓" if sqlite_count == mysql_count else "✗"
                if status == "✗":
                    all_ok = False
                print(f"  {status} {tname}: SQLite={sqlite_count}  MySQL={mysql_count}")

    if all_ok:
        log("All row counts match! Migration successful.")
    else:
        log("WARNING: Some row counts do not match. Check the ✗ entries above.")
    return all_ok


def main():
    log("=" * 60)
    log("  SkillBridge SQLite → MySQL Migration")
    log("=" * 60)
    log(f"SQLite path:  {SQLITE_PATH}")
    log(f"MySQL URL:    {MYSQL_URL.replace('://', '://***:***@')}")

    # ── Setup engines ──────────────────────────────────────────
    sqlite_engine = get_sqlite_engine()
    mysql_engine = get_mysql_engine()

    # ── Reflect SQLite tables ──────────────────────────────────
    sqlite_meta = MetaData()
    reflect_tables_from_engine(sqlite_engine, sqlite_meta)
    sqlite_tables = set(sqlite_meta.tables.keys())
    log(f"Tables in SQLite: {sorted(sqlite_tables)}")

    # ── Get model metadata and create MySQL tables ─────────────
    model_meta = get_model_tables()
    model_tables = set(model_meta.tables.keys())
    log(f"Tables in model metadata: {sorted(model_tables)}")
    create_tables_in_mysql(mysql_engine, model_meta)

    # ── Refresh MySQL metadata to reflect created tables ───────
    mysql_meta = MetaData()
    reflect_tables_from_engine(mysql_engine, mysql_meta)
    mysql_tables = set(mysql_meta.tables.keys())
    log(f"Tables now in MySQL: {sorted(mysql_tables)}")

    # ── Determine tables to migrate ────────────────────────────
    to_migrate = [t for t in TABLE_ORDER if t in sqlite_tables and t in model_tables]
    extras = sorted(
        (sqlite_tables & model_tables) - set(TABLE_ORDER)
    )
    to_migrate.extend(extras)
    log(f"Migration table order: {to_migrate}")

    # ── Copy data ──────────────────────────────────────────────
    log("\n── Copying data ──")
    total_rows = 0
    with sqlite_engine.connect() as s_conn:
        with mysql_engine.begin() as m_conn:
            m_conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            for tname in to_migrate:
                rows = copy_table(s_conn, m_conn, model_meta, tname)
                total_rows += rows
            m_conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    log(f"\nTotal rows copied: {total_rows}")

    # ── Validate ───────────────────────────────────────────────
    validate_counts(sqlite_engine, mysql_engine, model_meta)

    log("\n" + "=" * 60)
    log("  Migration complete!")
    log("=" * 60)
    log("\nNext steps:")
    log("  1. Update your .env file with DATABASE_URL=mysql+pymysql://...")
    log("  2. Start the application: python run.py")
    log("  3. Verify health: curl http://localhost:5000/health")
    log("  4. Log in and verify your data is intact")


if __name__ == "__main__":
    main()
