import pytest
from uuid import UUID
from stockforge.execution_identity import ExecutionIdentityError, execution_id_for_job, is_execution_uuid


def test_same_job_always_gets_same_execution_id():
    first = execution_id_for_job("project-1", "job-1")
    second = execution_id_for_job("project-1", "job-1")
    assert first == second
    assert is_execution_uuid(first)
    UUID(first)


def test_different_jobs_do_not_share_execution_id():
    assert execution_id_for_job("project-1", "job-1") != execution_id_for_job("project-1", "job-2")


def test_identity_requires_non_empty_values():
    with pytest.raises(ExecutionIdentityError): execution_id_for_job("", "job-1")
    with pytest.raises(ExecutionIdentityError): execution_id_for_job("project-1", "")
