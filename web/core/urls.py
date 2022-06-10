from django.urls import path

from core.views import Home

app_name = "core"

urlpatterns = [
    path('', Home.as_view(),
         name='home'),
]
