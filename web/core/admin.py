import uuid
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Task
from document.models import Document

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_user', 'view_topic', 'is_completed', 'num_ans',
        'view_best_answer', 'tags', 'created_at')

    list_filter = ['is_completed', 'user__username', 'created_at']
    search_fields = ['user__username', 'topic__uuid']


    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def view_topic(self, obj):
        url = reverse("admin:topic_topic_change", args=(obj.topic.id,))
        return format_html('<a href="{}">{}</a>', url, obj.topic.uuid)

    def view_best_answer(self, obj):
        if not obj.best_answers:
            return None
        best_answer = obj.best_answers.split('--')[1:]
        admin_best_ans = ""
        for i, ans in enumerate(best_answer):
            temp = ans.split("|")[:-1]
            if temp:
                admin_best_ans += f'\n\Grade {i+1}:\n\n'
            for doc in temp:
                d = Document.objects.get(uuid=doc)
                url = reverse("admin:document_document_change", args=(d.id,))
                admin_best_ans += f"(<a href={url}>{doc}</a>)"
        
        return format_html(admin_best_ans)

    view_user.short_description = "user"
    view_topic.short_description = "topic"
    view_best_answer.short_description = "Best Answer"