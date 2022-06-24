from django.urls import path
from django.urls.conf import re_path

from inquiry.views import BestAnswersView, InquiryCompleteView

app_name = "inquiry"

urlpatterns = [
    re_path(r'^best_answer/(?P<user_id>\d+)/(?P<judgment_id>\d+)/', BestAnswersView.as_view(),
         name='best_answer'),

    re_path(r'^inquiry_complete/(?P<user_id>\d+)/(?P<inquiry_id>\d+)/', InquiryCompleteView.as_view(),
         name='inquiry_complete'),
]
