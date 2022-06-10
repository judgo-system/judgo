
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from judgment.models import Judgment
from user.models import User
from interfaces import pref
from .models import Question, Inquiry



class InquiryView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'inquiry.html'

    def get_context_data(self, **kwargs):
        context = super(InquiryView, self).get_context_data(**kwargs)
        context["questions"] = Question.objects.all()
        
        return context

    def get(self, request, *args, **kwargs):
        return super(InquiryView, self).get(self, request, *args, **kwargs)


    def post(self, request, *args, **kwargs):

        if "selected_question" in self.request.POST: 

            question = Question.objects.get(
                    question_id=self.request.POST["selected_question"].strip()
            )
            state = pref.create_new_pref_obj(question)
                
            inquiry, created = Inquiry.objects.get_or_create(
                    question=question, 
                    session=self.request.user.active_session
            )

            if inquiry.is_completed:
                judgement = Judgment.objects.get(
                        user=self.request.user,
                        session= self.request.user.active_session,
                        inquiry=inquiry, 
                        is_complete=True, 
                    )
            else:

                judgement = Judgment.objects.create(
                        user=self.request.user,
                        session= self.request.user.active_session,
                        inquiry=inquiry,
                        state=state,
                        is_initialized=True
                    )

            user = User.objects.get(id=self.request.user.id)
            user.latest_judgment = judgement
            user.save()

            return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:judgment', 
                        kwargs = {"user_id" : user.id, "judgment_id": judgement.id}
                    )
                )

        return HttpResponseRedirect(
                    reverse_lazy(
                        'inquiry:inquiry', 
                        kwargs = {"user_id" : self.request.user.id, 
                        "session_id": self.request.user.active_session.id}
                    )
                )