from django.urls import path
from django.urls.conf import re_path

from judgment.views import JudgmentView

app_name = "judgment"

urlpatterns = [
    path('', JudgmentView.as_view(),
         name='judgment'),
    re_path(r'^(?P<user_id>\d+)/(?P<judgment_id>\d+)/', JudgmentView.as_view(),
         name='judgment'),
]
