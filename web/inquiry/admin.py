from django.contrib import admin

from .models import Question
# , Inquiry

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'content')
    search_fields = ['question_id']

