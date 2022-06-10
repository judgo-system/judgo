from django.urls import path
from django.urls.conf import re_path

from inquiry.views import InquiryView

app_name = "inquiry"

urlpatterns = [
    re_path(r'^(?P<user_id>\d+)/(?P<session_id>\d+)/', InquiryView.as_view(),
         name='inquiry'),
]
