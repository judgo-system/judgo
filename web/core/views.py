import logging
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.conf import settings


from .models import Task
from judgment.models import Judgment
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
            .filter(user_id=self.request.user, is_completed=False)\
            .order_by('created_at')
            

        if tasks:
            context["tasks"] = tasks
            context["message"] = 'Select a topic to review.'      
        else:
            context["message"] = 'There is no topic to review right now.'      


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
            prev_judge = Judgment.objects.filter(
                    user = self.request.user.id,
                    task=task.id
            ).order_by('id').latest('id')
            state = prev_judge.before_state
            if prev_judge.after_state:
                state = prev_judge.after_state
        except Exception as e:
            logger.warning(f"There is no previous judgment for topic={topic.title} and user={self.request.user.username}")
            state = pref.create_new_pref_obj(topic, settings.TOP_DOC_THRESHOULD)
                    
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
  


class SingleRoundResultsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'single_round_results.html'

    def get_context_data(self, **kwargs):
        context = super(SingleRoundResultsView, self).get_context_data(**kwargs)

        prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])
        context['question_content'] = prev_judge.task.topic.title
        answer_list = prev_judge.best_answers.split('--')[-1].split('|')[:-1]
        documets = []
        for answer in answer_list:
            documets.append(Document.objects.get(uuid=answer, topics=prev_judge.task.topic))
            
        context['documents'] = documets
        return context


    def post(self, request, *args, **kwargs):

        user = User.objects.get(id=request.user.id)
        prev_judge = user.latest_judgment

        if 'no' in request.POST:
            return HttpResponseRedirect(reverse_lazy('core:home'))

        elif 'prev' in request.POST: 
            judgement = user.latest_judgment
            # remove the best answer so far in case of changes
            prev_judge.task.best_answers = '--'.join(x for x in prev_judge.task.best_answers.split("--")[:-1])
            prev_judge.task.save()

        if 'yes' in request.POST:
            judgement = Judgment.objects.create(
                    user=user,
                    task=prev_judge.task,
                    before_state=prev_judge.after_state,
                    parent=prev_judge,
                    best_answers = prev_judge.best_answers
                )
            user.latest_judgment = judgement
            user.save()
        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {"user_id" : user.id, "judgment_id": judgement.id}
                )
        ) 



class TaskResultsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'task_results.html'

    def get_context_data(self, **kwargs):
        context = super(TaskResultsView, self).get_context_data(**kwargs)

        task = Task.objects.get(id=self.kwargs['task_id'])
        context['question_content'] = task.topic.title
        
        answer_list = {}
        for i, answer in enumerate(task.best_answers.split('--')[1:]):
            answer_list[i+1] = answer
         
        for k, v in answer_list.items():
            documets = []

            for doc in v.split('|')[:-1]:    
               documets.append(Document.objects.get(uuid=doc, topics=task.topic))

            answer_list[k] = documets        
        
        context['answer_list'] = answer_list
        return context



    def post(self, request, *args, **kwargs):

        return HttpResponseRedirect(
                reverse_lazy(
                    'core:home', 
                )
        ) 