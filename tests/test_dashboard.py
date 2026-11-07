from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]

def test_dashboard_empty_audience():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not at.exception
    assert at.metric[0].value=='4,264'
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception and at.metric[0].value=='0'
