from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]

def test_dashboard_empty_audience():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not at.exception
    assert at.metric[0].value=='4,264'
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception and at.metric[0].value=='0'

def test_dashboard_navigation_reset_and_segment_drilldown():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not at.exception
    assert at.metric[1].value=='3'
    # Cards use current filters and navigate to that same audience on export.
    next(b for b in at.button if b.label=='View Audience').click().run()
    assert not at.exception and at.radio[0].value=='Audience Export'
    assert at.metric[0].value=='703' and at.metric[1].value=='1'
    at.sidebar.button[2].click().run()
    assert not at.exception and at.metric[0].value=='4,264'
    for page in ['Manual RFM Baseline','Campaign Playbook','Cluster Evidence','Assign An RFM CSV','Segment Overview']:
        at.radio[0].set_value(page).run()
        assert not at.exception,page
    at.sidebar.button[1].click().run()
    assert not at.exception and at.metric[0].value=='0' and at.metric[1].value=='0'
    at.sidebar.button[0].click().run()
    assert not at.exception and at.metric[0].value=='4,264'

    # Empty audiences remain safe on every data-driven workspace.
    at.sidebar.button[1].click().run()
    for page in ['Manual RFM Baseline','Campaign Playbook','Audience Export','Cluster Evidence','Assign An RFM CSV']:
        at.radio[0].set_value(page).run()
        assert not at.exception,page
