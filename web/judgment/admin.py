from django.contrib import admin
from .models import Judgment

@admin.register(Judgment)
class JudgmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'parent_id', 'task_id',
        'is_initialized', 'is_round_done', 'is_complete',
        'action', 'created_at'
    )
    search_fields = ['user_id', 'task_id', 'is_complete']