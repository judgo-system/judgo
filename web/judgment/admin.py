from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from document.models import Document
from .models import Judgment
from .actions import export_task_as_csv_action


@admin.register(Judgment)
class JudgmentAdmin(admin.ModelAdmin):
    actions = [export_task_as_csv_action("CSV Export", fields=['id', 'user__username'])]
    list_display = ('id', 'view_user', 'parent_id', 'view_task', 'view_left_response', 'view_right_response',
        'view_best_answer', 'is_round_done', 'is_complete', 
        'action', 'created_at', 'completed_at'
    )

    search_fields = ['user__username', 'task__topic__title']
    list_filter = ['is_complete', 'task__topic__uuid']
    
    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def view_task(self, obj):
        url = reverse("admin:core_task_change", args=(obj.task.id,))
        return format_html('<a href="{}">Task ({})</a>', url, obj.task.topic.title)

    def view_left_response(self, obj):
        if not obj.left_response:
            return None
        url = reverse("admin:document_response_change", args=(obj.left_response.id,))
        return format_html('<a href="{}">({})</a>', url, obj.left_response.document.uuid)


    def view_right_response(self, obj):
        if not obj.right_response:
            return None
        url = reverse("admin:document_response_change", args=(obj.right_response.id,))
        return format_html('<a href="{}">({})</a>', url, obj.right_response.document.uuid)

    def view_best_answer(self, obj):
        if not obj.best_answers:
            return None
        best_answer = obj.best_answers.split('--')[1:]
        admin_best_ans = ""
        for i, ans in enumerate(best_answer):
            temp = ans.split("|")[:-1]
            if temp:
                admin_best_ans += f'\n\n Grade {i+1}:\n\n'
            for doc in temp:
                d = Document.objects.get(uuid=doc, topics=obj.task.topic)
                url = reverse("admin:document_document_change", args=(d.id,))
                admin_best_ans += f"(<a href={url}>{doc}</a>)"
        
        return format_html(admin_best_ans)
    
    view_best_answer.short_description = "Best Answer"

    view_user.short_description = "user"
    view_task.short_description = "task"
    view_left_response.short_description = "Left response"
    view_right_response.short_description = "Right response"


