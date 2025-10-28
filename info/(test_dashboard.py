import dash
from monitor import app

def test_app_starts(dash_duo):
    app.layout 
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("h1", "Mini LogicMonitor Casero")
    assert dash_duo.find_element("h1").text == "Mini LogicMonitor Casero"
