from django.contrib import admin

from .models import Question, Inquiry

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'content')
    search_fields = ['question_id']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'question_id', 'tags',
        'best_answers', 'is_completed')
    search_fields = ['question_id', 'is_completed']