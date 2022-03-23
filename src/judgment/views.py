from ast import arg
from pydoc import Doc
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from document.models import Documents
from question.models import Question
from judgment.models import Judgment, JudgingChoices
from interfaces import pref


class JudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'judgment.html'
    pref_obj = None


    def get_context_data(self, **kwargs):
        context = super(JudgmentView, self).get_context_data(**kwargs)
        print("GET CONTEXT")
        
        if "question_id" in kwargs and 'user_id' in kwargs:
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.filter(
                user__id=kwargs['user_id'], 
                question__id=kwargs['question_id']
            ).latest()

            (left, right) = pref.get_documents(prev_judge.state)
            context['question_id'] = prev_judge.question.question_id
            context['question_content'] = prev_judge.question.content
            context['left_id'] = left
            context['left_txt'] = Documents.objects.get(uuid=left).content
            context['right_id'] = right
            context['right_txt'] = Documents.objects.get(uuid=right).content
        return context

    def get(self, request, *args, **kwargs):
        print("GET")
        print(kwargs)

        if "question_id" in kwargs and 'user_id' in kwargs:
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.filter(
                user__id=kwargs['user_id'], 
                question__id=kwargs['question_id']
            ).latest()

            if pref.is_finish(prev_judge.state):
                return HttpResponseRedirect(reverse_lazy('core:home'))
        return super(JudgmentView, self).get(self, request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        
        print("POST")
        print(request.POST)
        question = Question.objects.get(question_id=request.POST["question_id"])
        prev_judge = Judgment.objects.filter(
                user__id=request.user.id, 
                question__id=question.id
            ).latest()

        state = None
        action = None
        if 'left' in request.POST:
            action = JudgingChoices.LEFT
            state = pref.evaluate(prev_judge.state, request.POST['left_doc_id'])
        elif 'right' in request.POST:
            action = JudgingChoices.RIGHT
            state = pref.evaluate(prev_judge.state, request.POST['right_doc_id'])
        elif 'equal' in request.POST:

            action = JudgingChoices.EQUAL
            state = pref.evaluate(prev_judge.state, request.POST['right_doc_id'], equal=True)
        
        if state:
            doc_left = Documents.objects.get(uuid=request.POST['left_doc_id'])
            doc_right = Documents.objects.get(uuid=request.POST['right_doc_id'])

            Judgment.objects.create(
                    user=request.user,
                    question=question,
                    state=state,
                    action=action,
                    doc_left=doc_left,
                    doc_right=doc_right
                )

            return HttpResponseRedirect(reverse_lazy('judgment:judgment', kwargs = {"user_id" : request.user.id, "question_id": question.id}))
        return HttpResponseRedirect(reverse_lazy('judgment:judgment'))