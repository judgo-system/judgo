from django.urls import path
from django.urls.conf import re_path

from judgment.views import JudgmentView
from judgment.debug_view import DebugJudgmentView

app_name = "judgment"

urlpatterns = [
    path('', JudgmentView.as_view(),
         name='judgment'),
    re_path(r'^(?P<user_id>\d+)/(?P<judgment_id>\d+)/$', JudgmentView.as_view(),
         name='judgment'),
    re_path(r'^(?P<user_id>\d+)/(?P<judgment_id>\d+)/debug/', DebugJudgmentView.as_view(),
         name='debug'),
]
