from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user_id', 'question_id', 'tags', 'num_ans',
        'best_answers', 'is_completed')
    search_fields = ['user_id', 'question_id', 'is_completed']