from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import Home, SingleRoundResultsView, TaskResultsView

class TestUrls(SimpleTestCase):
    
    def test_home_url_is_resolved(self):
        
        url = reverse('core:home')
        self.assertEquals(resolve(url).func.view_class, Home)

    def test_single_round_results_url_is_resolved(self):
        url = reverse('core:single_round_results', args=[1, 1])
        self.assertEquals(resolve(url).func.view_class, SingleRoundResultsView)

    def test_task_results_url_is_resolved(self):
        url = reverse('core:task_results', args=[1, 1])
        self.assertEquals(resolve(url).func.view_class, TaskResultsView)