import os
import pytest
import unified


RUN_ONLINE = os.getenv('RUN_ONLINE') == '1'


@pytest.mark.skipif(not RUN_ONLINE, reason="Online tests disabled. Set RUN_ONLINE=1 to enable")
@pytest.mark.online
def test_online_invoices():
    """Run the sample invoice numbers against the live endpoints.

    Note: this test is skipped by default. To run it, set the environment
    variable RUN_ONLINE=1 and execute pytest. These tests can fail due to
    network errors, remote site changes, or rate limiting (they are intended
    for manual/e2e checks, not as flaky CI gates).
    """
    invoices = [
        ("404931271275", "Lotte"),
        ("363225021454", "CUpost"),
        ("210535605545", "CVSNet"),
    ]

    for inv, expect in invoices:
        res = unified.track(inv, debug=True)
        assert isinstance(res, dict), f"Expected dict for {inv}, got {type(res)}"
        assert 'error' not in res, f"Online track returned error for {inv}: {res.get('error')}"
        # basic sanity: tracking number should appear
        tn = res.get('tracking_number') or res.get('tracking')
        assert tn and str(inv) in str(tn)
