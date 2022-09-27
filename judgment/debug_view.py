import logging
from braces.views import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.conf import settings

from judgment.models import Judgment, JudgingChoices
from interfaces import pref
from .views import JudgmentView


logger = logging.getLogger(__name__)

class DebugJudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'judgment.html'
    
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
        
        
        context = super(DebugJudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])

            if prev_judge.is_complete:
                context["task_status"] = "complete"
                return context

            self.task_id = prev_judge.task.id

            context['topic'] = prev_judge.task.topic
            context['font_size'] = prev_judge.task.font_size
            
            # if there is no tag is we don't need to fill it out.
            if prev_judge.task.tags:
                # modifyed tag inorder to work according Tagify information
                context['highlights'] = prev_judge.task.tags
            

            (context, left_response, right_response) = JudgmentView.get_documents_related_context(context, self.request.user, prev_judge)
            
            self.left_doc_id = left_response.id
            self.right_doc_id = right_response.id

            context['left_txt'] = f"{left_response.document.content}"
            context['right_txt'] = f"{right_response.document.content}"

            if left_response.document.title:
                context['left_txt'] = f"Title: {left_response.document.title} \n"\
                        f"Document ID: {left_response.document.uuid}\n\n"\
                        f"{context['left_txt']}"
            
            if right_response.document.title:
                context['right_txt'] = f"Title: {right_response.document.title}\n"\
                        f"Document ID: {right_response.document.uuid}\n\n"\
                        f"{context['righ_txt']}"
                        
            #debug part
            context["debug"] = "true"
            if prev_judge.parent and prev_judge.parent.action:
                context['previous_action'] = dict(JudgingChoices.choices)[prev_judge.parent.action]
            context['tree_content'] = pref.get_str(prev_judge.before_state)
            
            
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

        if prev_judge.is_tested:
            judgment = JudgmentView.handle_test_judgment(prev_judge, action)
            user.latest_judgment = judgment
            user.save()
            
            return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:debug', 
                    kwargs = {"user_id" : user.id, "judgment_id": judgment.id}
                )
            )

        # the user is back to the same judment so we need to make a copy of this    
        if prev_judge.action != None:
            logger.info(f"User change their mind about judment {prev_judge.id} which was {prev_judge.action}")
            prev_judge.has_changed = True
            prev_judge.save()
            parent_best_answer = None
            if prev_judge.parent:
                parent_best_answer = prev_judge.parent.best_answers
            prev_judge = Judgment.objects.create(
                user=user,
                task=prev_judge.task,
                before_state=prev_judge.before_state,
                parent=prev_judge.parent,
                left_response=prev_judge.left_response,
                right_response=prev_judge.right_response,
                best_answers=parent_best_answer
            )
            
        logger.info(f"This user had action: {prev_judge.action} about judment {prev_judge.id}")

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

    
            if pref.is_judgment_completed(after_state) or prev_judge.task.num_ans >= settings.TOP_DOC_THRESHOULD:
                prev_judge.is_complete = True
                prev_judge.task.is_completed = True
                prev_judge.task.best_answers = prev_judge.best_answers
                prev_judge.task.save()
                prev_judge.save()

                return HttpResponseRedirect(
                    reverse_lazy(
                        'topic:inquiry_complete', 
                        kwargs = {"user_id" : user.id, "task_id": prev_judge.task.id}
                    )
                ) 

            #     return HttpResponseRedirect(
            #     reverse_lazy(
            #         'judgment:judgment', 
            #         kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
            #     )
            # )

        # if prev_judge.is_round_done:
        #     logger.info(f'One round is finished! you are going to the next step!')


        if prev_judge.is_round_done:
            
            return HttpResponseRedirect(
                reverse_lazy(
                    'topic:best_answer', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            ) 
        # for deep learning trec we want a test judgment feature
        prev_judge, is_test = JudgmentView.get_fake_test_judgment(user, prev_judge)
        

        judgement = Judgment.objects.create(
                user=user,
                task=prev_judge.task,
                before_state=after_state,
                parent=prev_judge
            )

        if is_test:
            user.latest_judgment = prev_judge
            user.save() 
            return HttpResponseRedirect(
            reverse_lazy(
                'judgment:debug', 
                kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
            )
        )
        else: 
            user.latest_judgment = judgement
            user.save()
            return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:debug', 
                    kwargs = {"user_id" : user.id, "judgment_id": judgement.id}
                )
            )
            
   