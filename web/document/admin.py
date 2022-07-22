from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Document, Response


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'content', 'view_topic')
    search_fields = ['uuid', "topic__uuid", 'content']

    def view_topic(self, obj):
        url = reverse("admin:topic_topic_change", args=(obj.topic.id,))
        return format_html('<a href="{}">{}</a>', url, obj.topic.uuid)

    view_topic.short_description = "topic"

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_document', 'view_user', 'highlight')
    
    search_fields = ['document__uuid', 'user__username']

    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)


    def view_document(self, obj):
        
        url = reverse("admin:response_document_change", args=(obj.document.id,))
        return format_html('<a href="{}">({})</a>', url, obj.document.uuid)

    view_user.short_description = "user"
    view_document.short_description = "Document"
