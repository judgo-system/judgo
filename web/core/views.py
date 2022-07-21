import logging
import pickle
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from judgment.models import RelevantJudgmentChoices

from .models import Task
from judgment.models import Step1Judgment, Step2Judgment, Step3Judgment
from topic.models import Topic
from user.models import User
from document.models import Document
from interfaces import pref

logger = logging.getLogger(__name__)

class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)

        tasks = Task.objects\
            .filter(user_id=self.request.user, step3_checked=False)\
            .order_by('updated_at')
            

        if tasks:
            context["tasks"] = tasks
            context["message"] = 'Please pick one of the following quesions to review.'      
        else:
            context["task_exist"] = 'false'
            context["message"] = 'There is no quesiton to review right now.'      


        return context

    def get(self, request, *args, **kwargs):

        # if user is an admin it should reroute to admin page 
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

        
        if not task.step1_checked:
            return self.create_or_get_step1_judgment(task, topic)
        elif not task.step2_checked:
            return self.create_or_get_step2_judgment(task, topic)
        else:
            return self.create_or_get_step3_judgment(task, topic)



    def create_or_get_step1_judgment(self, task, topic):

        prev_judge = None

        try:
            prev_judge = Step1Judgment.objects.filter(
                    user = self.request.user.id,
                    task=task.id
            ).order_by('id').latest('id')
            
            state = prev_judge.state
        except Exception as e:
            logger.warning(f"There is no previous judgment for topic={topic.title} and user={self.request.user.username}")
            documents = list( Document.objects.filter(
                topics__uuid = topic.uuid
            ).values_list('uuid', flat=True))
            state = pickle.dumps(documents)
            task.num_doc_step1 = len(documents)
            task.save()



        if not prev_judge:

            prev_judge = Step1Judgment.objects.create(
                    user=self.request.user,
                    task=task,
                    state=state,
                )
        user = User.objects.get(id=self.request.user.id)
        # user.latest_judgment = prev_judge
        user.save()

        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:step1', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )
  
    def create_or_get_step2_judgment(self, task, topic):

        prev_judge = None

        try:
            prev_judge = Step2Judgment.objects.filter(
                    user=self.request.user.id,
                    task=task.id
            ).order_by('id').latest('id')
            
            state = prev_judge.state
        except Exception as e:
            logger.warning(f"There is no previous judgment for topic={topic.title} and user={self.request.user.username}")
            documents = list(Step1Judgment.objects.filter(
                user=self.request.user.id,
                task=task.id,
                action=RelevantJudgmentChoices.YES
            ).values_list('response__document__uuid', flat=True))
            state = pickle.dumps(documents)
            task.num_doc_step2 = len(documents)
            task.save()



        if not prev_judge:

            prev_judge = Step2Judgment.objects.create(
                    user=self.request.user,
                    task=task,
                    state=state,
                )
        user = User.objects.get(id=self.request.user.id)
        # user.latest_judgment = prev_judge
        user.save()

        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:step2', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )
  
    def create_or_get_step3_judgment(self, task, topic):

        prev_judge = None

        try:
            prev_judge = Step3Judgment.objects.filter(
                    user = self.request.user.id,
                    task=task.id
            ).order_by('id').latest('id')
            state = prev_judge.before_state
            if prev_judge.after_state:
                state = prev_judge.after_state
        except Exception as e:
            logger.warning(f"There is no previous judgment for topic={topic.title} and user={self.request.user.username}")
            
            logger.warning(f"There is no previous judgment for topic={topic.title} and user={self.request.user.username}")
            documents = list(Step2Judgment.objects.filter(
                user=self.request.user.id,
                task=task.id,
                action=RelevantJudgmentChoices.YES
            ).values_list('response__document__uuid', flat=True))
            state = pref.create_new_pref_obj(documents)


        if not prev_judge or prev_judge.is_complete:

            prev_judge = Step3Judgment.objects.create(
                    user=self.request.user,
                    task=task,
                    before_state=state,
                    parent=prev_judge,
                )
        user = User.objects.get(id=self.request.user.id)
        user.latest_judgment = prev_judge
        user.save()

        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:step3', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )
  