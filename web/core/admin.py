from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_user', 'view_question', 'is_completed', 'num_ans',
        'best_answers', 'tags', 'created_at')

    list_filter = ['is_completed', 'user__username', 'created_at']
    search_fields = ['user__username', 'question__question_id']


    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def view_question(self, obj):
        url = reverse("admin:inquiry_question_change", args=(obj.question.id,))
        return format_html('<a href="{}">{}</a>', url, obj.question.question_id)

    view_user.short_description = "user"
    view_question.short_description = "question"