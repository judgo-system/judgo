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
            task_id = self.request.POST["selected_question"]
        
            task = Task.objects\
                .get(id=task_id)
            topic = Topic.objects.get(id=task.topic.id)

            judge = None
            try:
                judge = Judgment.objects.filter(
                        user = self.request.user.id,
                        task=task.id
                ).order_by('id').latest('id')
                state = judge.before_state
                if judge.after_state:
                    state = judge.after_state
            except Exception as e:
                logger.warning(f"There is no previous judgment for topic={topic.title} and user={self.request.user.username}")
                state = pref.create_new_pref_obj(topic, settings.TOP_DOC_THRESHOULD)
                        
            if not judge or judge.is_complete:

                judge = Judgment.objects.create(
                        user=self.request.user,
                        task=task,
                        before_state=state,
                        parent=judge,
                        best_answers = ""
                    )
            user = User.objects.get(id=self.request.user.id)
            user.latest_judgment = judge
            user.save()

            return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:judgment', 
                        kwargs = {"user_id" : user.id, "judgment_id": judge.id}
                    )
                )
    


class SingleRoundResultsView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'single_round_results.html'

    def get_context_data(self, **kwargs):
        context = super(SingleRoundResultsView, self).get_context_data(**kwargs)

        judge = Judgment.objects.get(id=self.kwargs['judgment_id'])
        context['question_content'] = judge.task.topic.title
        
        parent_judge = judge.parent
        
        complete_round_number = len(judge.best_answers.split('--'))
        if parent_judge:
            prev_round_number = len(parent_judge.best_answers.split("--"))
            complete_round_number -= prev_round_number
        

        answer_list = {}
        for answer in judge.best_answers.split('--')[-complete_round_number:]:
            answer_list[prev_round_number] = answer
            prev_round_number+=1
        
        for k, v in answer_list.items():
            documets = []

            for doc in v.split('|')[:-1]:    
               documets.append(Document.objects.get(uuid=doc, topics=judge.task.topic))

            answer_list[k] = documets        
        
        print(answer_list)
        context['round_answer_list'] = answer_list
        return context


    def post(self, request, *args, **kwargs):

        user = User.objects.get(id=request.user.id)
        judge = user.latest_judgment

        if 'no' in request.POST:
            return HttpResponseRedirect(reverse_lazy('core:home'))

        elif 'prev' in request.POST: 
            judgement = user.latest_judgment
            # remove the best answer so far in case of changes
            judge.task.best_answers = '--'.join(x for x in judge.task.best_answers.split("--")[:-1])
            judge.task.save()

        if 'yes' in request.POST:
            judgement = Judgment.objects.create(
                    user=user,
                    task=judge.task,
                    before_state=judge.after_state,
                    parent=judge,
                    best_answers = judge.best_answers
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

