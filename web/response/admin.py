from django.contrib import admin
from .models import Document, Response


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'content')
    search_fields = ['uuid']


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_id', 'session_id', 'highlight')
    search_fields = ['document_id']