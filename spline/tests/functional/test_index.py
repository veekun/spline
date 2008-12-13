from spline.tests import *

class TestIndexController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='index', action='index'))
        # Test response...
