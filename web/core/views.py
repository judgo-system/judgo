import logging
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from datetime import datetime
from .models import Task
from judgment.models import Judgment
from topic.models import Topic
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
            context["message"] = 'Select a topic to review.'      
        else:
            context["message"] = 'There is no topic to review right now.'      

        logger.info(f"User = '{self.request.user.username}' is at Home page")

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
        topic = Topic.objects.get(id=task.topic.id)

        prev_judge = None
        try:
            logger.info(f"Topic = '{topic.title}' is being judged by user = '{self.request.user.username}'")
            prev_judge = Judgment.objects.filter(
                    user = self.request.user.id,
                    task=task.id
            ).order_by('id').latest('id')
            state = prev_judge.before_state
            if prev_judge.after_state:
                state = prev_judge.after_state
        except Exception as e:
            logger.warning(f"There is no previous judgment for topic = '{topic.title}' by user = '{self.request.user.username}'")
            state = pref.create_new_pref_obj(topic)
                    
        if not prev_judge or prev_judge.is_complete:

            prev_judge = Judgment.objects.create(
                    user=self.request.user,
                    task=task,
                    before_state=state,
                    parent=prev_judge,
                    best_answers = ""
                )
        user = User.objects.get(id=self.request.user.id)
        user.latest_judgment = prev_judge
        user.save()

        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )
  