from django.contrib import admin
from .models import Document, Response


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'content', 'base_question')
    search_fields = ['uuid']


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_id', 'user_id', 'highlight')
    search_fields = ['document_id']