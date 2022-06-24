import math
import re
from urllib import request
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from response.models import Document, Response
from judgment.models import Judgment, JudgingChoices
from user.models import User
from interfaces import pref

class JudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'judgment.html'
    # pref_obj = None
    task_id = None
    left_doc_id = None
    right_doc_id = None


    def render_to_response(self, context, **response_kwargs):

        response = super().render_to_response(context, **response_kwargs)

        # for taging and highlighting purpose
        response.set_cookie("task_id", self.task_id)
        response.set_cookie("left_doc_id", self.left_doc_id)
        response.set_cookie("right_doc_id", self.right_doc_id)

        return response


    def get_context_data(self, **kwargs):
        
        context = super(JudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])
            self.task_id = prev_judge.task.id
            (left, right) = pref.get_documents(prev_judge.before_state)
            
            context['question_content'] = prev_judge.task.question.content
            context["progress_bar_width"] = self.get_progress_count(prev_judge)
            context['state_object'] = pref.get_str(prev_judge.before_state)
            
            context['left_id'] = left
            context['right_id'] = right

            left_doc = Document.objects.get(uuid=left)
            right_doc = Document.objects.get(uuid=right)
            left_response, _ = Response.objects.get_or_create(user=self.request.user, document=left_doc)
            right_response, _ = Response.objects.get_or_create(user=self.request.user, document=right_doc)
            self.left_doc_id = left_response.id
            self.right_doc_id = right_response.id

            if left_response.highlight:
                context['left_txt'] = self.highlight_document(
                    left_response.document.content,
                    left_response.highlight
                ) 
            else:
                context['left_txt'] = left_response.document.content
                
            if right_response.highlight:
                context['right_txt'] = self.highlight_document(
                    right_response.document.content,
                    right_response.highlight
                ) 
            else:
                context['right_txt'] = right_response.document.content

                
            # if there is no tag is we don't need to fill it out.
            if prev_judge.task.tags:
                context['highlights'] = prev_judge.task.tags

        return context


    def post(self, request, *args, **kwargs):
        
        if 'prev' in request.POST: 
            return self.handle_prev_button(request.user, request.user.latest_judgment)

        elif 'left' in request.POST or 'right' in request.POST or 'equal' in request.POST:
            return self.handle_judgment_actions(request.user, request.user.latest_judgment, request.POST)
        
        return HttpResponseRedirect(reverse_lazy('core:home'))


    def add_new_answer(self, state, task):
        best_docs = pref.get_best(state)

        prev_ans = task.best_answers if task.best_answers else "" 
        new_ans = ""

        for doc in best_docs:
            # if doc in new_ans:
            #     new_ans = new_ans.replace(f'{doc}|', '')
            new_ans += doc + "|"

        task.best_answers = prev_ans +"--"+new_ans
        task.save()

        return best_docs


    def handle_prev_button(self, user, prev_judge):

        if prev_judge.parent:    
            user.latest_judgment = prev_judge.parent
            user.save()
            return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:judgment', 
                        kwargs = {"user_id" : user.id, "judgment_id": prev_judge.parent.id}
                    )
                )

        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )

    
    def handle_judgment_actions(self, user, prev_judge, requested_action):

        # print(f'before judgment: {pref.get_str(prev_judge.before_state)}')
        action, after_state = self.evaluate_after_state(requested_action, prev_judge.before_state)

        # the user is back to the same judment so we need to make a copy of this    
        if prev_judge.action != None:
            
            # print(f"User change their mind about judment {prev_judge.id} which was {prev_judge.action}")
            prev_judge = Judgment.objects.create(
                user=user,
                task=prev_judge.task,
                before_state=prev_judge.before_state,
                parent=prev_judge.parent
            )
            
        
        # update pre_judge action
        prev_judge.action = action
        prev_judge.after_state = after_state
        prev_judge.save()

        # print(f'after judgment: {pref.get_str(prev_judge.after_state)}')

        # check if this round of judgment is finished or not!
        while pref.is_judgment_finished(after_state):

            answer = self.add_new_answer(after_state, prev_judge.task)
            
            # print(f'best answer so far: {answer}')

            prev_judge.is_round_done = True
            after_state = pref.pop_best(after_state)
            prev_judge.after_state = after_state
            prev_judge.save()

            # print(f'after judgment: {pref.get_str(prev_judge.after_state)}')
    
            if pref.is_judgment_completed(after_state):
                prev_judge.is_complete = True
                prev_judge.task.is_completed = True

                prev_judge.task.save()
                prev_judge.save()

                # go back to home!
                return HttpResponseRedirect(
                    reverse_lazy(
                        'core:home'
                    )
                )  
  

        if prev_judge.is_round_done:
            
            return HttpResponseRedirect(
                reverse_lazy(
                    'inquiry:best_answer', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )    

        judgement = Judgment.objects.create(
                user=user,
                task=prev_judge.task,
                before_state=after_state,
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


    def evaluate_after_state(self, requested_action, before_state):
        action, after_state = None, None

        (left, right) = pref.get_documents(before_state)

        if 'left' in requested_action:
            action = JudgingChoices.LEFT
            after_state = pref.evaluate(before_state, left)
        elif 'right' in requested_action:
            action = JudgingChoices.RIGHT
            after_state = pref.evaluate(before_state, right)
        else:
            action = JudgingChoices.EQUAL
            after_state = pref.evaluate(before_state, right, equal=True)
        
        return action, after_state


    
    def highlight_document(self, text, highlight):

        if not highlight:
            return text
        highlights = highlight.split("|||")

        for part in highlights:
            if part:
                text = text.replace(part, "<span class = 'highlight'>{}</span>".format(part))
        return text


    def get_progress_count(self, prev_judge):

        total_doc = Document.objects.filter(
            base_question=prev_judge.task.question.id
        ).count()        
        remaining = pref.get_size(prev_judge.before_state)

        return str(math.floor(( total_doc - remaining) / total_doc * 100) )




class DebugJudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'judgment_debug.html'


    def get_context_data(self, **kwargs):
        
        context = super(DebugJudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:            
            prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])
            tree = pref.get_str(prev_judge.before_state).split("[")[0]
            context['tree'] = tree
        return context

