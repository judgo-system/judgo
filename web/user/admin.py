from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.utils.html import format_html
from .models import User


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(User)
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
            ('User Profile', {'fields': ('first_name', 'last_name', 'username')}),
    ) + AuthUserAdmin.fieldsets
    fieldsets = (
            ('User Profile', {'fields': ('name', )}),
    ) + AuthUserAdmin.fieldsets

    list_display = ('username', 'is_superuser', 'last_active_time', \
        'view_latest_judgment')
    list_filter = ['is_superuser', 'last_active_time']
    search_fields = ['username']

    def view_latest_judgment(self, obj):
        if not obj.latest_judgment:
            return None
        id = obj.latest_judgment.id
        url = reverse("admin:judgment_judgment_change", args=(id,))
        
        return format_html('<a href="{}">{} Judgment</a>', url, id)


    view_latest_judgment.short_description = "latest judgment"
