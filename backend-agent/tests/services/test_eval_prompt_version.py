from app.modules.evals.service import result_prompt_version


def test_result_prompt_version_reads_versioning_step():
    workflow_steps = [
        {"agent": "supervisor_agent", "action": "意图分类完成", "detail": {}},
        {"agent": "versioning", "action": "prompt_version_recorded", "detail": {"prompt_version": "v1"}},
    ]

    assert result_prompt_version(workflow_steps) == "v1"
