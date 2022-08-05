import html
import logging
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from document.models import Document, Response
from judgment.models import Judgment, JudgingChoices
from .views import JudgmentView
from interfaces import pref


logger = logging.getLogger(__name__)

class DebugJudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'judgment.html'
    
    task_id = None
    left_doc_id = None
    right_doc_id = None
    TOP_DOC_THRESHOULD = 10


    def render_to_response(self, context, **response_kwargs):

        response = super().render_to_response(context, **response_kwargs)

        # for taging and highlighting purpose
        response.set_cookie("task_id", self.task_id)
        response.set_cookie("left_doc_id", self.left_doc_id)
        response.set_cookie("right_doc_id", self.right_doc_id)

        return response


    def get_context_data(self, **kwargs):
        
        context = super(DebugJudgmentView, self).get_context_data(**kwargs)
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])
            
            if prev_judge.is_complete:
                context["task_status"] = "complete"
                return context

            context["debug"] = "true"

            self.task_id = prev_judge.task.id
            (left, right) = pref.get_documents(prev_judge.before_state)
            
            context['question_content'] = prev_judge.task.topic.title

            if prev_judge.parent and prev_judge.parent.action:
                context['previous_action'] = dict(JudgingChoices.choices)[prev_judge.parent.action]
            context['tree_content'] = pref.get_str(prev_judge.before_state)
            
            context["progress_bar_width"] = pref.get_progress_count(prev_judge.before_state)
            
            context['state_object'] = pref.get_str(prev_judge.before_state)

            context['topic'] = prev_judge.task.topic    
            context['support'] = prev_judge.task.topic.uuid.split("_")[1].upper()

            left_doc = Document.objects.get(uuid=left, topics=prev_judge.task.topic)
            right_doc = Document.objects.get(uuid=right, topics=prev_judge.task.topic)
            left_response, _ = Response.objects.get_or_create(user=self.request.user, document=left_doc)
            right_response, _ = Response.objects.get_or_create(user=self.request.user, document=right_doc)
            
            context['doc_left'] = left_response.document
            context['doc_right'] = right_response.document


            prev_judge.left_response = left_response
            prev_judge.right_response = right_response
            prev_judge.best_answers = prev_judge.parent.best_answers if prev_judge.parent else ""

            prev_judge.save()

            self.left_doc_id = left_response.id
            self.right_doc_id = right_response.id

            if left_response.highlight:
                context['left_txt'] = JudgmentView.highlight_document(
                    left_response.document.content,
                    left_response.highlight
                ) 
            else:
                context['left_txt'] = left_response.document.content
                
            if right_response.highlight:
                context['right_txt'] = JudgmentView.highlight_document(
                    right_response.document.content,
                    right_response.highlight
                ) 
            else:
                context['right_txt'] = right_response.document.content

            # if there is no tag is we don't need to fill it out.
            if prev_judge.task.tags:
                # modifyed tag inorder to work according Tagify information
                context['highlights'] = prev_judge.task.tags.replace(",", ".").replace("-", ",")

        return context


    def post(self, request, *args, **kwargs):
        
        if 'prev' in request.POST: 
            return self.handle_prev_button(request.user, request.user.latest_judgment)

        elif 'left' in request.POST or 'right' in request.POST or 'equal' in request.POST:
            return self.handle_judgment_actions(request.user, request.user.latest_judgment, request.POST)
        
        return HttpResponseRedirect(reverse_lazy('core:home'))




    def handle_prev_button(self, user, prev_judge):

        if prev_judge.parent:    
            user.latest_judgment = prev_judge.parent
            user.save()
            return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:debug', 
                        kwargs = {"user_id" : user.id, "judgment_id": prev_judge.parent.id}
                    )
                )
        return HttpResponseRedirect(
                reverse_lazy(
                    'core:home')
            )

    
    def handle_judgment_actions(self, user, prev_judge, requested_action):

        action, after_state = JudgmentView.evaluate_after_state(requested_action, prev_judge.before_state)

        # the user is back to the same judment so we need to make a copy of this    
        if prev_judge.action != None:
            
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

        # check if this round of judgment is finished or not!
        while pref.is_judgment_finished(after_state):

            prev_judge.best_answers = JudgmentView.append_answer(after_state, prev_judge)
            prev_judge.task.num_ans = len(prev_judge.best_answers.split("|")) - 1
            prev_judge.task.save()           
            prev_judge.is_round_done = True
            after_state = pref.pop_best(after_state)
            prev_judge.after_state = after_state
            prev_judge.save()

    
            if pref.is_judgment_completed(after_state) or prev_judge.task.num_ans >= self.TOP_DOC_THRESHOULD:
                

                prev_judge.task.best_answers = prev_judge.best_answers        
                prev_judge.is_complete = True
                prev_judge.task.is_completed = True
                prev_judge.task.save()
                prev_judge.save()

                return HttpResponseRedirect(
                    reverse_lazy(
                        'topic:inquiry_complete', 
                        kwargs = {"user_id" : user.id, "task_id": prev_judge.task.id}
                    )
                ) 
            

        if prev_judge.is_round_done:
            
            return HttpResponseRedirect(
                reverse_lazy(
                    'topic:best_answer', 
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
                'judgment:debug', 
                kwargs = {"user_id" : user.id, "judgment_id": judgement.id,}
            )
        )


