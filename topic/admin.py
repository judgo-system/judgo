from django.contrib import admin

from .models import Topic

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'num_related_document', 'title')
    search_fields = ['uuid', 'title']