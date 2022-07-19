from django.contrib import admin

from .models import Topic
# , Inquiry

@admin.register(Topic)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'title')
    search_fields = ['uuid', 'title']

