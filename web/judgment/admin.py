from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Judgment, JudgmentConsistency

@admin.register(Judgment)
class JudgmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_user', 'parent_id', 'view_task', 'view_left_response', 'view_right_response',
        'is_initialized', 'is_round_done', 'is_complete', 'has_changed', 'is_tested',
        'action', 'created_at'
    )

    search_fields = ['user__username', 'task__question__content']
    list_filter = ['is_complete', 'task__question__question_id']
    
    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def view_task(self, obj):
        url = reverse("admin:core_task_change", args=(obj.task.id,))
        return format_html('<a href="{}">Task ({})</a>', url, obj.task.question.content)

    def view_left_response(self, obj):
        if not obj.left_response:
            return None
        url = reverse("admin:response_response_change", args=(obj.left_response.id,))
        return format_html('<a href="{}">({})</a>', url, obj.left_response.document.uuid)


    def view_right_response(self, obj):
        if not obj.right_response:
            return None
        url = reverse("admin:response_response_change", args=(obj.right_response.id,))
        return format_html('<a href="{}">({})</a>', url, obj.right_response.document.uuid)

    view_user.short_description = "user"
    view_task.short_description = "task"
    view_left_response.short_description = "Left response"
    view_right_response.short_description = "Right response"




@admin.register(JudgmentConsistency)
class JudgmentConsistencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_user', 'view_task', 'view_judgment', 'previous_action',
        'current_action', 'created_at'
    )

    search_fields = ['user__username']
    
    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def view_task(self, obj):
        url = reverse("admin:core_task_change", args=(obj.task.id,))
        return format_html('<a href="{}">Task ({})</a>', url, obj.task.question.content)


    def view_judgment(self, obj):
        if not obj.judgment:
            return None
        id = obj.judgment.id
        url = reverse("admin:judgment_judgment_change", args=(id,))
        
        return format_html('<a href="{}">{} Judgment</a>', url, id)

    view_user.short_description = "user"
    view_task.short_description = "task"
    view_judgment.short_description = "judgment"
