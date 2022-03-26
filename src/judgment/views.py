from ast import arg
from pydoc import Doc
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from document.models import Documents
from question.models import Question
from judgment.models import Judgment, JudgingChoices
from users.models import User

from interfaces import pref


class JudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'judgment.html'
    pref_obj = None


    def get_context_data(self, **kwargs):
        
        context = super(JudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.get(id=kwargs['judgment_id'])

            (left, right) = pref.get_documents(prev_judge.state)
            context['question_id'] = prev_judge.question.question_id
            context['question_content'] = prev_judge.question.content
            context['left_id'] = left
            context['left_txt'] = Documents.objects.get(uuid=left).content
            context['right_id'] = right
            context['right_txt'] = Documents.objects.get(uuid=right).content
        return context

    def get(self, request, *args, **kwargs):
        print("=======================================")
        print("GET")
        print(kwargs)

        if "judgment_id" in kwargs and 'user_id' in kwargs:
            prev_judge = Judgment.objects.get(id=kwargs['judgment_id'])

            if pref.is_finish(prev_judge.state):
                return HttpResponseRedirect(reverse_lazy('core:home'))
        return super(JudgmentView, self).get(self, request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        
        print("POST")
        
        print(request.POST)

        user = User.objects.get(id=request.user.id)
        prev_judge = user.latest_judgment

        if 'prev' in request.POST: 
            if prev_judge.parent:
            
                user.latest_judgment = prev_judge.parent
                user.save()

                return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:judgment', 
                        kwargs = {"user_id" : user.id, "judgment_id": prev_judge.parent.id}
                    )
                )
            else:
                return HttpResponseRedirect(reverse_lazy('core:home'))
                

        # get documents 
        (left, right) = pref.get_documents(prev_judge.state)

        state = None
        action = None
        if 'left' in request.POST:
            action = JudgingChoices.LEFT
            state = pref.evaluate(prev_judge.state, left)
        elif 'right' in request.POST:
            action = JudgingChoices.RIGHT
            state = pref.evaluate(prev_judge.state, right)
        elif 'equal' in request.POST:
            action = JudgingChoices.EQUAL
            state = pref.evaluate(prev_judge.state, right, equal=True)
        
        if state:
            doc_left = Documents.objects.get(uuid=left)
            doc_right = Documents.objects.get(uuid=right)

            judgement = Judgment.objects.create(
                    user=request.user,
                    question=prev_judge.question,
                    state=state,
                    action=action,
                    doc_left=doc_left,
                    doc_right=doc_right,
                    parent=prev_judge
                )

            user.latest_judgment = judgement
            user.save()

            return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {"user_id" : user.id, "judgment_id": judgement.id}
                )
            )
        
        return HttpResponseRedirect(reverse_lazy('judgment:judgment'))


    