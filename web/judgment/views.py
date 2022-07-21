from copyreg import pickle
import logging
import random
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from document.models import Document, Response
from judgment.models import Step3Judgment
from interfaces import pref
from . import helper
# from web.judgment.models import RelevantJudgmentChoices, Step1Judgment


logger = logging.getLogger(__name__)

class Step3JudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'dual_judgment.html'
    # pref_obj = None
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
        
        context = super(Step3JudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            # get the latest judment for this user and question
            prev_judge = Step3Judgment.objects.get(id=self.kwargs['judgment_id'])
            
            if prev_judge.is_complete:
                context["task_status"] = "complete"
                return context

            self.task_id = prev_judge.task.id
            (left, right) = pref.get_documents(prev_judge.before_state)
            

            context['question_content'] = prev_judge.task.topic.title

            context["progress_bar_width"] = pref.get_progress_count(prev_judge.before_state)
            
            context['state_object'] = pref.get_str(prev_judge.before_state)
            
            context['left_id'] = left
            context['right_id'] = right

            left_doc = Document.objects.get(uuid=left)
            right_doc = Document.objects.get(uuid=right)
            left_response, _ = Response.objects.get_or_create(user=self.request.user, document=left_doc)
            right_response, _ = Response.objects.get_or_create(user=self.request.user, document=right_doc)

            prev_judge.left_response = left_response
            prev_judge.right_response = right_response
            prev_judge.save()

            self.left_doc_id = left_response.id
            self.right_doc_id = right_response.id

            if left_response.highlight:
                context['left_txt'] = helper.highlight_document(
                    left_response.document.content,
                    left_response.highlight
                ) 
            else:
                context['left_txt'] = left_response.document.content
                
            if right_response.highlight:
                context['right_txt'] = helper.highlight_document(
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




    def handle_prev_button(self, user, prev_judge):

        if prev_judge.parent:    
            user.latest_judgment = prev_judge.parent
            user.save()
            return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:step3', 
                        kwargs = {"user_id" : user.id, "judgment_id": prev_judge.parent.id}
                    )
                )

        return HttpResponseRedirect(
                reverse_lazy(
                    'core:home' 
                )
            )

    
    def handle_judgment_actions(self, user, prev_judge, requested_action):
        """
        """
        action, after_state = helper.evaluate_after_state(requested_action, prev_judge.before_state)

        # the user is back to the same judment so we need to make a copy of this    
        if prev_judge.action != None:
            logger.info(f"User change their mind about judment {prev_judge.id} which was {prev_judge.action}")
            prev_judge = Step3Judgment.objects.create(
                user=user,
                task=prev_judge.task,
                before_state=prev_judge.before_state,
                parent=prev_judge.parent
            )
            
        logger.info(f"This user had action: {prev_judge.action} about judment {prev_judge.id}")

        # update pre_judge action
        prev_judge.action = action
        prev_judge.after_state = after_state
        prev_judge.save()

        # check if this round of judgment is finished or not!
        while pref.is_judgment_finished(after_state):

            helper.add_new_answer(after_state, prev_judge.task)
            
            prev_judge.is_round_done = True
            after_state = pref.pop_best(after_state)
            prev_judge.after_state = after_state
            prev_judge.save()

    
            if pref.is_judgment_completed(after_state) or prev_judge.task.num_ans >= self.TOP_DOC_THRESHOULD:
                prev_judge.is_complete = True
                prev_judge.task.step3_checked = True

                prev_judge.task.save()
                prev_judge.save()

                return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:step3', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )

        if prev_judge.is_round_done:
            logger.info(f'One round is finished! you are going to the next step!')

        judgement = Step3Judgment.objects.create(
                user=user,
                task=prev_judge.task,
                before_state=after_state,
                parent=prev_judge
            )

        user.latest_judgment = judgement
        user.save()
        return HttpResponseRedirect(
            reverse_lazy(
                'judgment:step3', 
                kwargs = {"user_id" : user.id, "judgment_id": judgement.id}
            )
        )


        
        


    

    



