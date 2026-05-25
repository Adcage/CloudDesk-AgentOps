"""CI 环境中初始化 eval 数据库

执行顺序：
1. 创建 business / agent schema
2. 执行 init.sql 建表
3. 执行 seed.sql + seed_enterprise_v1.sql 导入种子数据
4. 执行 hybrid_search.sql 建立全文检索
5. 导入知识库文档到向量库
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = PROJECT_ROOT / "sql"
BACKEND_AGENT = PROJECT_ROOT / "backend-agent"

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/clouddesk",
)


def _run_sql_file(conn, filepath: Path):
    print(f"  Running: {filepath.name}")
    sql_content = filepath.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql_content)
    conn.commit()


def _wait_for_db() -> bool:
    for attempt in range(30):
        try:
            conn = psycopg2.connect(
                host=os.environ.get("PGHOST", "localhost"),
                port=int(os.environ.get("PGPORT", "5432")),
                user=os.environ.get("PGUSER", "postgres"),
                password=os.environ.get("PGPASSWORD", "postgres"),
                dbname=os.environ.get("PGDATABASE", "clouddesk"),
            )
            conn.close()
            print("PostgreSQL is ready.")
            return True
        except psycopg2.OperationalError:
            print(f"Waiting for PostgreSQL... ({attempt + 1}/30)")
            time.sleep(2)
    return False


def main():
    if not _wait_for_db():
        print("ERROR: PostgreSQL did not become ready in time.")
        sys.exit(1)

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", "postgres"),
        dbname=os.environ.get("PGDATABASE", "clouddesk"),
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    try:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS business")
            cur.execute("CREATE SCHEMA IF NOT EXISTS agent")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()

        sql_files = [
            SQL_DIR / "init.sql",
            SQL_DIR / "seed.sql",
            SQL_DIR / "seed_enterprise_v1.sql",
            SQL_DIR / "hybrid_search.sql",
        ]
        for f in sql_files:
            if f.exists():
                _run_sql_file(conn, f)

        print("Database initialized successfully.")

        print("Ingesting knowledge base documents...")
        subprocess.run(
            [sys.executable, "-m", "app.rag.ingest"],
            cwd=str(BACKEND_AGENT),
            check=False,
        )
        print("Knowledge base ingestion completed.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
