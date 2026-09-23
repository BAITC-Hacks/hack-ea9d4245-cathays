import pytest

@pytest.fixture(autouse=True)
def no_live_provider(monkeypatch):
    """Tests must opt into a scripted transport; never spend API credits."""
    def blocked(*args, **kwargs):
        raise AssertionError("Unexpected live provider request in a test")
    monkeypatch.setattr("app.routing.provider_client.urlopen", blocked)
