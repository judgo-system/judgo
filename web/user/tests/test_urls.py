from django.test import SimpleTestCase
from django.urls import reverse, resolve
from user.views import UserUpdateView, UserProfile, UserUpdateView, UserRedirectView, UserDetailView

class TestUrls(SimpleTestCase):

    
    def test_user_update_url_is_resolved(self):
        url = reverse('user:update', args=[1])
        self.assertEquals(resolve(url).func.view_class, UserUpdateView)

    def test_user_profile_url_is_resolved(self):
        url = reverse('user:profile', args=[1])
        self.assertEquals(resolve(url).func.view_class, UserProfile)

    def test_user_update_url_is_resolved(self):
        url = reverse('user:update', args=[1])
        self.assertEquals(resolve(url).func.view_class, UserUpdateView)

    def test_user_redirect_url_is_resolved(self):     
        url = reverse('user:redirect')
        self.assertEquals(resolve(url).func.view_class, UserRedirectView)   

    def test_user_detail_url_is_resolved(self): 
        url = reverse('user:user_detail', args=[1])
        self.assertEquals(resolve(url).func.view_class, UserDetailView)


    
    