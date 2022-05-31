
import re
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from judgment.models import Judgment
from inquiry.models import Question
from user.models import User
from interfaces import pref
from .models import Session


class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        # context["questions"] = Question.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        if not self.request.user.active_session:
            session = Session.objects.create(
                name='first session',
                username = self.request.user
            )
            self.request.user.active_session = session
            self.request.user.save()

        return super(Home, self).get(self, request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        
        
        print(f"Post things ===========>{self.request.POST}")
        if "start_question_judment" in self.request.POST:
            
            return HttpResponseRedirect(
                reverse_lazy(
                    'inquiry:inquiry', 
                    kwargs = {"user_id" : self.request.user.id, 
                        "session_id": self.request.user.active_session.id}
                )
            )

        return HttpResponseRedirect(reverse_lazy('core:home'))

