from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from topic.models import Topic
from .models import Document, Response


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'title', 'url',  'view_topics')
    search_fields = ['uuid', 'title', 'url']

    def view_topics(self, obj):
        if not obj.topics.all:
            return None
        admin_topics = ""
        for i, t in enumerate(obj.topics.all()):
            topic = Topic.objects.get(uuid=t.uuid)
            url = reverse("admin:topic_topic_change", args=(topic.id,))
            admin_topics += f"(<a href={url}>{topic.uuid}</a>)"
        
        return format_html(admin_topics)

    view_topics.short_description = "topics"

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_document', 'view_user', 'highlight')
    
    search_fields = ['document__uuid', 'user__username']

    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)


    def view_document(self, obj):
        
        url = reverse("admin:document_document_change", args=(obj.document.id,))
        return format_html('<a href="{}">({})</a>', url, obj.document.uuid)

    view_user.short_description = "user"
    view_document.short_description = "Document"