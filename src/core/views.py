
import re
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from judgment.models import Judgment
from question.models import Question
from interfaces import pref

class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context["questions"] = Question.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        return super(Home, self).get(self, request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        
        if "selected_question" in self.request.POST: 
            # print(f"Haaaaa {self.request.POST['selected_question'].strip()}")
            question = Question.objects.get(question_id=self.request.POST["selected_question"].strip())
            state = pref.create_new_pref_obj(question)

            Judgment.objects.create(
                user=request.user,
                question=question,
                state=state,
                is_initialized=True
            )

            return HttpResponseRedirect(
                reverse_lazy('judgment:judgment', kwargs = {"user_id" : request.user.id, "question_id": question.id}))

        return HttpResponseRedirect(reverse_lazy('core:home'))
