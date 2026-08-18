import pytest

from stockforge.generation import GenerationError, GenerationRequest, GenerationResult


def test_generation_request_round_trip_shape():
    request = GenerationRequest(
        prompt="commercial lifestyle photo of a modern workspace",
        negative_prompt="text, watermark, logo",
        width=1536,
        height=1024,
        steps=28,
        guidance_scale=6.5,
        seed=42,
        batch_size=4,
        model_id="example.model",
        model_version="1.0",
        workflow_hash="workflow123",
        input_artifact_ids=("ref-1",),
        parameters={"sampler": "euler"},
    )

    data = request.to_dict()

    assert data["schema_version"] == 1
    assert data["input_artifact_ids"] == ["ref-1"]
    assert data["parameters"] == {"sampler": "euler"}


def test_generation_request_rejects_invalid_values():
    with pytest.raises(GenerationError, match="prompt"):
        GenerationRequest(prompt="   ")
    with pytest.raises(GenerationError, match="width"):
        GenerationRequest(prompt="test", width=0)
    with pytest.raises(GenerationError, match="steps"):
        GenerationRequest(prompt="test", steps=0)
    with pytest.raises(GenerationError, match="batch_size"):
        GenerationRequest(prompt="test", batch_size=101)
    with pytest.raises(GenerationError, match="seed"):
        GenerationRequest(prompt="test", seed=-1)


def test_success_result_requires_artifact():
    with pytest.raises(GenerationError, match="at least one artifact"):
        GenerationResult(status="succeeded")


def test_success_result_rejects_error_fields():
    with pytest.raises(GenerationError, match="cannot contain an error"):
        GenerationResult(
            status="succeeded",
            artifact_ids=("a1",),
            error_code="PROVIDER_ERROR",
            error_message="bad",
        )


def test_failed_result_requires_structured_error():
    with pytest.raises(GenerationError, match="requires error_code"):
        GenerationResult(status="failed")


def test_failed_result_is_serializable():
    result = GenerationResult(
        status="failed",
        provider_job_id="provider-42",
        error_code="TIMEOUT",
        error_message="provider timed out",
    )
    assert result.to_dict()["status"] == "failed"
    assert result.to_dict()["error_code"] == "TIMEOUT"
