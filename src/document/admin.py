from django.contrib import admin
from .models import Documents



@admin.register(Documents)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'content')
    search_fields = ['uuid']
