
from pdb import post_mortem
import re
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .models import Task
from judgment.models import Judgment
from inquiry.models import Question
from user.models import User
from interfaces import pref


class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):

        # if user is an admin it should reroute to admin page 
        if request.user.is_superuser:
            return HttpResponseRedirect(reverse_lazy('admin:index'))

        # for reviewer 
        else:
            # retreive available task
            tasks = Task.objects\
                .filter(user_id=request.user, is_completed=False)\
                .order_by('created_at')
            
            print(tasks)

            if tasks:
                return self.start_judgment(tasks[0])

        # if not self.request.user.active_session:
            # session = Session.objects.create(
            #     name='first session',
            #     username = self.request.user
            # )

            # self.request.user.active_session = session

        return super(Home, self).get(self, request, *args, **kwargs)


    def start_judgment(self, task):

        print(f' iyooo->> {task.question}')
        question = Question.objects.get(id=task.question.id)
        # inquiry, created = Inquiry.objects.get_or_create(
        #         question=question, 
        #         session=self.request.user.active_session
        # )

        prev_judge = None
        try:
            prev_judge = Judgment.objects.filter(
                    user = self.request.user.id,
                    task=task.id
            ).order_by('id').latest('id')
            state = prev_judge.before_state
            if prev_judge.after_state:
                state = prev_judge.after_state
        except Exception as e:
            print(f" There is no previous judgment for this question and user")
            state = pref.create_new_pref_obj(question)


        if not prev_judge or not prev_judge.is_complete:

            judgement = Judgment.objects.create(
                    user=self.request.user,
                    task=task,
                    before_state=state,
                    parent=prev_judge,
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
  



    # def post(self, request, *args, **kwargs):
        
    #     if "start_question_judment" in self.request.POST:
    #         return HttpResponseRedirect(
    #             reverse_lazy(
    #                 'inquiry:inquiry', 
    #                 kwargs = {"user_id" : self.request.user.id, 
    #                     "session_id": self.request.user.active_session.id}
    #             )
    #         )
        
    #     elif "continue_question_judment" in self.request.POST:
            
    #         judgement = self.request.user.latest_judgment
    #         return HttpResponseRedirect(
    #             reverse_lazy(
    #                 'judgment:judgment', 
    #                 kwargs = {
    #                     "user_id" : self.request.user.id, 
    #                     "judgment_id": judgement.id
    #                 }
    #             )
    #         )


    #     elif "start_new_session" in self.request.POST:
            
    #         name = self.request.user.name + "-new-session"            
    #         if 'session_name' in self.request.POST:
    #             name = self.request.POST['session_name']
            
    #         # session = Session.objects.create(
    #         #     name=name,
    #         #     username = self.request.user
    #         # )

    #         # self.request.user.active_session = session
    #         self.request.user.save()

    #     return HttpResponseRedirect(reverse_lazy('core:home'))

