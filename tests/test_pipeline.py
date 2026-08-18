from types import SimpleNamespace

import pytest

from stockforge.pipeline import PipelineDefinition, PipelineError, PipelineRunner, PipelineStep
from stockforge.plugin import PluginDescriptor, PluginRegistry


class EchoPlugin:
    descriptor = PluginDescriptor(
        id="test.echo",
        name="Test Echo",
        version="1.0.0",
        kind="processor",
        capabilities=frozenset({"echo"}),
    )

    def execute(self, payload):
        return {"received": payload}

    def healthcheck(self):
        return True


class FailingPlugin:
    descriptor = PluginDescriptor(
        id="test.fail",
        name="Test Failure",
        version="1.0.0",
        kind="processor",
        capabilities=frozenset({"fail"}),
    )

    def execute(self, payload):
        raise RuntimeError("boom")

    def healthcheck(self):
        return False


def test_pipeline_serialization_contract():
    step = PipelineStep("step-1", "test.echo", "echo", parameters={"quality": 2})
    definition = PipelineDefinition("demo.pipeline", 1, (step,), metadata={"purpose": "test"})
    data = definition.to_dict()
    assert data["schema_version"] == 1
    assert data["steps"][0]["parameters"] == {"quality": 2}


def test_pipeline_rejects_duplicate_step_ids():
    step = PipelineStep("same", "test.echo", "echo")
    with pytest.raises(PipelineError, match="step ids must be unique"):
        PipelineDefinition("demo.pipeline", 1, (step, step))


def test_runner_executes_steps_in_order():
    registry = PluginRegistry()
    registry.register(EchoPlugin())
    definition = PipelineDefinition(
        "demo.pipeline",
        1,
        (PipelineStep("step-1", "test.echo", "echo"),),
    )
    result = PipelineRunner(registry).run(definition, {"input": {"value": 42}})
    assert result.completed_steps == ("step-1",)
    assert result.outputs["output"]["received"]["value"] == 42
    assert result.outputs["output"]["received"]["parameters"] == {}


def test_runner_rejects_missing_capability():
    registry = PluginRegistry()
    registry.register(EchoPlugin())
    definition = PipelineDefinition(
        "demo.pipeline",
        1,
        (PipelineStep("step-1", "test.echo", "missing"),),
    )
    with pytest.raises(PipelineError, match="does not provide capability"):
        PipelineRunner(registry).run(definition, {"input": {}})


def test_runner_wraps_plugin_failure():
    registry = PluginRegistry()
    registry.register(FailingPlugin())
    definition = PipelineDefinition(
        "demo.pipeline",
        1,
        (PipelineStep("step-1", "test.fail", "fail"),),
    )
    with pytest.raises(PipelineError, match="Pipeline step 'step-1' failed"):
        PipelineRunner(registry).run(definition, {"input": {}})
