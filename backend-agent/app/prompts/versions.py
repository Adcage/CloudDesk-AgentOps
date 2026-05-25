from pathlib import Path


CURRENT_VERSIONS = {
    "supervisor": "v1",
    "billing": "v1",
    "account": "v1",
    "approval": "v1",
    "fact_check": "v1",
    "memory_summarize": "v1",
    "rerank_select": "v1",
}


def load_prompt(name: str) -> tuple[str, str]:
    version = CURRENT_VERSIONS.get(name, "v1")
    prompt_path = Path(__file__).resolve().parent / f"{name}_{version}.txt"
    return prompt_path.read_text(encoding="utf-8").strip(), version
