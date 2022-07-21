from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Step3Judgment, Step1Judgment, Step2Judgment

@admin.register(Step3Judgment)
class Step3JudgmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_user', 'parent_id', 'view_task', 'view_left_response', 'view_right_response',
        'is_initialized', 'is_round_done', 'is_complete', 
        'action', 'created_at'
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

    view_user.short_description = "user"
    view_task.short_description = "task"
    view_left_response.short_description = "Left response"
    view_right_response.short_description = "Right response"



@admin.register(Step1Judgment)
class Step1JudgmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_user', 'previous_id', 'view_task', 'view_response',
        'is_complete', 'action', 'created_at'
    )

    search_fields = ['user__username', 'task__topic__title']
    list_filter = ['is_complete', 'task__topic__uuid']
    
    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def view_task(self, obj):
        url = reverse("admin:core_task_change", args=(obj.task.id,))
        return format_html('<a href="{}">Task ({})</a>', url, obj.task.topic.title)

    def view_response(self, obj):
        if not obj.response:
            return None
        url = reverse("admin:document_response_change", args=(obj.response.id,))
        return format_html('<a href="{}">({})</a>', url, obj.response.document.uuid)


    view_user.short_description = "user"
    view_task.short_description = "task"
    view_response.short_description = "response"


@admin.register(Step2Judgment)
class Step2JudgmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_user', 'previous_id', 'view_task', 'view_response',
        'is_complete', 'action', 'created_at'
    )

    search_fields = ['user__username', 'task__topic__title']
    list_filter = ['is_complete', 'task__topic__uuid']
    
    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def view_task(self, obj):
        url = reverse("admin:core_task_change", args=(obj.task.id,))
        return format_html('<a href="{}">Task ({})</a>', url, obj.task.topic.title)

    def view_response(self, obj):
        if not obj.response:
            return None
        url = reverse("admin:document_response_change", args=(obj.response.id,))
        return format_html('<a href="{}">({})</a>', url, obj.response.document.uuid)


    view_user.short_description = "user"
    view_task.short_description = "task"
    view_response.short_description = "response"

