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
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from topic.api import add_tag, remove_tag, update_font_size, handle_popup
from document.api import add_highlight, remove_highlight

urlpatterns = [
    path('', include('core.urls', namespace='core')),
    path('topic/', include('topic.urls', namespace='topic')),
    path('judgment/', include('judgment.urls', namespace='judgment')),
    path('admin/', admin.site.urls),

    # User management
    path('user/', include('user.urls', namespace='user')),
    path('accounts/', include('allauth.urls')),

    path('update_font_size/<int:taskId>/', update_font_size, name='update_font_size'),
    path('add_tag/<int:taskId>/', add_tag, name='add_tag'),

    path('remove_tag/<int:taskId>/', remove_tag, name='remove_tag'),
    path('add_highlight/<int:responseId>/', add_highlight, name='add_highlight'),
    path('remove_highlight/<int:responseId>/', remove_highlight, name='remove_highlight'),

    path('popup_alert/<int:taskId>/', handle_popup, name ='handle_popup'),
]
