from app.tracing.timers import Timers

def test_total_and_status_are_interpretable():
    timers = Timers()
    with timers.measure("routing"):
        pass
    assert timers.result()["routing"]["status"] == "measured"
    assert timers.result()["total"]["duration_ms"] >= 0
