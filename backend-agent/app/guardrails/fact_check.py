import re

from sqlalchemy import text

from app.db.session import SessionLocal


def _document_exists(doc_name: str) -> bool:
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT 1 FROM agent.documents WHERE title = :title LIMIT 1"),
            {"title": doc_name},
        )
        return result.fetchone() is not None
    except Exception:
        return False
    finally:
        db.close()


def check_factual_claims(answer: str) -> tuple[bool, list[str]]:
    cited_docs = re.findall(r"([A-Za-z0-9_\-]+\.md)", answer or "")
    if not cited_docs:
        return True, []

    violations = []
    for doc_name in cited_docs:
        if not _document_exists(doc_name):
            violations.append(doc_name)

    return len(violations) == 0, violations
