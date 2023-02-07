from django.test import SimpleTestCase
from django.urls import reverse, resolve
from judgment.views import JudgmentView

class TestUrls(SimpleTestCase):

    def test_judgment_url_is_resolved(self):
        url = reverse('judgment:judgment')
        self.assertEquals(resolve(url).func.view_class, JudgmentView)
    
