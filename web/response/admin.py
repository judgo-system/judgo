from django.contrib import admin
from .models import Document



@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'content')
    search_fields = ['uuid']
