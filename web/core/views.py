
from pdb import post_mortem
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
        return context

    def get(self, request, *args, **kwargs):

        if request.user.is_superuser:
            return HttpResponseRedirect(reverse_lazy('admin:index'))

        if not self.request.user.active_session:
            session = Session.objects.create(
                name='first session',
                username = self.request.user
            )

            self.request.user.active_session = session
            self.request.user.save()

        return super(Home, self).get(self, request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        
        if "start_question_judment" in self.request.POST:
            return HttpResponseRedirect(
                reverse_lazy(
                    'inquiry:inquiry', 
                    kwargs = {"user_id" : self.request.user.id, 
                        "session_id": self.request.user.active_session.id}
                )
            )
        
        elif "continue_question_judment" in self.request.POST:
            
            judgement = self.request.user.latest_judgment
            return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {
                        "user_id" : self.request.user.id, 
                        "judgment_id": judgement.id
                    }
                )
            )


        elif "start_new_session" in self.request.POST:
            
            name = self.request.user.name + "-new-session"            
            if 'session_name' in self.request.POST:
                name = self.request.POST['session_name']
            
            session = Session.objects.create(
                name=name,
                username = self.request.user
            )

            self.request.user.active_session = session
            self.request.user.save()

        return HttpResponseRedirect(reverse_lazy('core:home'))

