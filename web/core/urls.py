from django.urls import path
from django.urls.conf import re_path

from core.views import Home, SingleRoundResultsView, TaskResultsView

app_name = "core"

urlpatterns = [
    path('', Home.as_view(),
         name='home'),
    re_path(r'^single_round_results/(?P<user_id>\d+)/(?P<judgment_id>\d+)/', SingleRoundResultsView.as_view(),
         name='single_round_results'),

    re_path(r'^task_results/(?P<user_id>\d+)/(?P<task_id>\d+)/', TaskResultsView.as_view(),
         name='task_results'),
]
