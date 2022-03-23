from django.urls import path
from django.urls.conf import re_path

from judgment.views import JudgmentView

app_name = "judgment"

urlpatterns = [
    path('', JudgmentView.as_view(),
         name='judgment'),
    path(r'^(?P<user_id>\w+)/(?P<question_id>\w+)/', JudgmentView.as_view(),
         name='judgment'),
]
