from spline.tests import *

class TestMainController(TestController):

    def test_main(self):
        response = self.app.get(url(controller='main', action='index'))
        # Test response...
