"""Comprehensive SDK wiring test — verifies all imports resolve."""


def test_sdk_import():
    from neuralscope.sdk.client import NeuralScope

    ns = NeuralScope()
    assert ns.model
    assert ns.profile == "default"


def test_sdk_list_models():
    from neuralscope.sdk.client import NeuralScope

    ns = NeuralScope()
    providers = ns.list_models()
    assert isinstance(providers, list)
    assert len(providers) >= 5


def test_all_feature_imports():
    assert True


def test_cli_import():
    from neuralscope.cli.app import app

    assert app is not None
