import logging
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from datetime import datetime
from .models import Task
from judgment.models import Judgment
from inquiry.models import Question
from user.models import User
from interfaces import pref

logger = logging.getLogger(__name__)

class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)


        tasks = Task.objects\
            .filter(user_id=self.request.user, is_completed=False)\
            .order_by('created_at')
            

        if tasks:
            context["tasks"] = tasks
            context["message"] = 'Please pick one of the following quesions to review.'      
        else:
            context["task_exist"] = 'false'
            context["message"] = 'There is no quesiton to review right now.'      

        if not self.request.user.first_login_time:
            self.request.user.first_login_time = datetime.now()
            self.request.user.save()
            context["instruction_visibility"] = "yes"

        return context

    def get(self, request, *args, **kwargs):

        if request.user.is_superuser:
            return HttpResponseRedirect(reverse_lazy('admin:index'))

        return super(Home, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        if "selected_question" in self.request.POST: 
            return self.start_judgment(self.request.POST["selected_question"])
        

    def start_judgment(self, task_id):

        task = Task.objects\
            .get(id=task_id)
        question = Question.objects.get(id=task.question.id)

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
            logger.warning(f"There is no previous judgment for question={question.content} and user={self.request.user.username}")
            state = pref.create_new_pref_obj(question)
                    
        if not prev_judge or prev_judge.is_complete:

            prev_judge = Judgment.objects.create(
                    user=self.request.user,
                    task=task,
                    before_state=state,
                    parent=prev_judge,
                )
        user = User.objects.get(id=self.request.user.id)
        user.latest_judgment = prev_judge
        # user.is_tested=False
        user.save()

        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )
  