
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from judgment.models import Judgment
from user.models import User
from document.models import Document
from core.models import Task


class BestAnswersView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'best_answer.html'

    def get_context_data(self, **kwargs):
        context = super(BestAnswersView, self).get_context_data(**kwargs)

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
                    parent=prev_judge
                )
            user.latest_judgment = judgement
            user.save()
        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:debug', 
                    kwargs = {"user_id" : user.id, "judgment_id": judgement.id}
                )
        ) 



class InquiryCompleteView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'inquiry_complete.html'

    def get_context_data(self, **kwargs):
        context = super(InquiryCompleteView, self).get_context_data(**kwargs)

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