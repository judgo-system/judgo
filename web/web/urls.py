"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from inquiry.api import add_tag, remove_tag
from response.api import add_highlight, remove_highlight

urlpatterns = [
    # path('', include('core.urls', namespace='core')),
    path('', include('core.urls', namespace='core')),
    path('inquiry/', include('inquiry.urls', namespace='inquiry')),
    path('judgment/', include('judgment.urls', namespace='judgment')),
    path('admin/', admin.site.urls),

    # User management
    path('user/', include('user.urls', namespace='user')),
    path('accounts/', include('allauth.urls')),

    path('add_tag/<int:inquiryId>/', add_tag, name='add_tag'),
    path('remove_tag/<int:inquiryId>/', remove_tag, name='remove_tag'),
    path('add_highlight/<int:responseId>/', add_highlight, name='add_highlight'),
    path('remove_highlight/<int:responseId>/', remove_highlight, name='remove_highlight'),

]
