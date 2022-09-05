
from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Task
from document.models import Document
from topic.models import Topic
from user.models import User
from .actions import export_task_as_csv_action


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    

    actions = [export_task_as_csv_action("CSV Export", fields=['id', 'user__username'])]

    list_display = ('id', 'view_user', 'view_topic', 'is_completed', 'num_ans', 'font_size',
        'view_best_answer', 'tags', 'created_at')

    list_filter = ['is_completed', 'user__username', 'created_at']
    search_fields = ['user__username', 'topic__uuid']


    def view_user(self, obj):
        url = reverse("admin:user_user_change", args=(obj.user.id,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def view_topic(self, obj):
        url = reverse("admin:topic_topic_change", args=(obj.topic.id,))
        return format_html('<a href="{}">{}</a>', url, obj.topic.title)

    def view_best_answer(self, obj):
        if not obj.best_answers:
            return None
        best_answer = obj.best_answers.split('--')[1:]
        admin_best_ans = ""
        for i, ans in enumerate(best_answer):
            temp = ans.split("|")[:-1]
            if temp:
                admin_best_ans += f'\n\n Grade {i+1}:\n\n'
            for doc in temp:
                d = Document.objects.get(uuid=doc, topics=obj.topic)
                url = reverse("admin:document_document_change", args=(d.id,))
                admin_best_ans += f"(<a href={url}>{doc}</a>)"
        
        return format_html(admin_best_ans)

    view_user.short_description = "user"
    view_topic.short_description = "topic"
    view_best_answer.short_description = "Best Answer"




    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls

    def upload_csv(self, request):

        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]
            print(csv_data)

            for i, x in enumerate(csv_data):
                fields = x.split(",")
                try:
                    user = User.objects.get(username=fields[0].strip())
                    topic = Topic.objects.get(uuid=fields[1].strip())
                    created = Task.objects.create(
                        user = user,
                        topic = topic,
                        )
                except Exception as e:
                    print(f"Row {i} cann't be ingested error message is {e}")

            url = reverse('admin:index')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)