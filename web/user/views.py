import json
import datetime
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from core.models import Task
from judgment.models import Judgment
from django.utils.safestring import SafeString

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("user:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("user:detail", kwargs={"username": self.request.user.username})


class UserProfile(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profile.html'

    def change_datetime(self, o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
            
    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)

        context["username"] = self.request.user.username
        context["email"] = self.request.user.email
        
        tasks = Task.objects\
            .filter(user_id=self.request.user)

        context["total_task"] = len(tasks)
        context["complete_task"] = len(tasks.exclude(is_completed=False))

        judgments = Judgment.objects\
            .filter(user_id=self.request.user)\
            .order_by('-id')

        context["total_judgment"] = len(judgments)        

        tasks_list = []
        for task in tasks:

            judgments = Judgment.objects\
                .filter(task=task)

            dic = [
                task.topic.title,
                "completed" if task.is_completed else "",
                task.created_at,
                len(judgments),
                judgments[0].created_at if judgments else "",
            ]
            tasks_list.append(dic)



        context["tasks_list"] = SafeString(json.dumps(tasks_list, sort_keys=True,
            indent=1,
            default=self.change_datetime))

        return context

    def get(self, request, *args, **kwargs):

        if request.user.is_superuser:
            return HttpResponseRedirect(reverse_lazy('admin:index'))

        return super(UserProfile, self).get(self, request, *args, **kwargs)

