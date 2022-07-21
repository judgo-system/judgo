from django.urls import path
from django.urls.conf import re_path

from judgment.views import Step3JudgmentView
from judgment.step1views import Step1JudgmentView
from judgment.step2views import Step2JudgmentView
from judgment.debug_view import DebugJudgmentView

app_name = "judgment"

urlpatterns = [
#     path('', Step1JudgmentView.as_view(),
#          name='judgment'),
    re_path(r'step1/(?P<user_id>\d+)/(?P<judgment_id>\d+)/$', Step1JudgmentView.as_view(),
         name='step1'),
     
    re_path(r'step2/(?P<user_id>\d+)/(?P<judgment_id>\d+)/$', Step2JudgmentView.as_view(),
         name='step2'),
     
    re_path(r'step3/(?P<user_id>\d+)/(?P<judgment_id>\d+)/$', Step3JudgmentView.as_view(),
         name='step3'),
    re_path(r'^(?P<user_id>\d+)/(?P<judgment_id>\d+)/debug/', DebugJudgmentView.as_view(),
         name='debug'),
]
