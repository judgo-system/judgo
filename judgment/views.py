import logging
import random
from braces.views import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.conf import settings

from document.models import Document, Response
from judgment.models import Judgment, JudgingChoices, JudgmentConsistency
from interfaces import pref

logger = logging.getLogger(__name__)

class JudgmentView(LoginRequiredMixin, generic.TemplateView):
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
        
        context = super(JudgmentView, self).get_context_data(**kwargs)
        
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

            context['left_txt'] = f"Document ID: {left_response.document.uuid}\n\n"\
                    f"{left_response.document.content}"


            context['right_txt'] = f"Document ID: {right_response.document.uuid}\n\n"\
                    f"{right_response.document.content}"

            if left_response.document.title:
                context['left_txt'] = f"Title: {left_response.document.title} \n" + context['left_txt']
            
            if right_response.document.title:
                context['right_txt'] = f"Title: {right_response.document.title}\n" +  context['right_txt']


        return context

    
    @staticmethod
    def get_documents_related_context(context, user, prev_judge):

   
        if prev_judge.is_tested:
            context["progress_bar_width"] = pref.get_progress_count(prev_judge.parent.after_state)
        
            # change the left and right documents
            right_response = prev_judge.left_response 
            left_response = prev_judge.right_response 

            
            # check if the following judgment documents are new or not 
            (left, right) = pref.get_documents(prev_judge.parent.after_state)
            left_doc = Document.objects.get(uuid=left, topics=prev_judge.task.topic)
            right_doc = Document.objects.get(uuid=right, topics=prev_judge.task.topic)
            left_new = Response.objects.filter(user=user, document=left_doc)
            right_new = Response.objects.filter(user=user, document=right_doc)
            
            # context['new_left'] = 'TEST '
            # context['new_right'] = 'TEST '
            if not len(left_new) or not len(right_new):
                context['new_left'] = 'NEW '
                context['new_right'] = 'NEW '
            else:           
                context['highlight_left_txt'] = left_response.highlight
                context['highlight_right_txt'] = right_response.highlight
            

        else:  
            (left, right) = pref.get_documents(prev_judge.before_state)
            left_doc = Document.objects.get(uuid=left, topics=prev_judge.task.topic)
            right_doc = Document.objects.get(uuid=right, topics=prev_judge.task.topic)         
            context["progress_bar_width"] = pref.get_progress_count(prev_judge.before_state)

            left_response, left_created = Response.objects.get_or_create(user=user, document=left_doc)
            right_response, right_created = Response.objects.get_or_create(user=user, document=right_doc)

            if left_created:
                context['new_left'] = 'NEW '
            
            if right_created:
                context['new_right'] = 'NEW '


            prev_judge.left_response = left_response
            prev_judge.right_response = right_response
            prev_judge.best_answers = prev_judge.parent.best_answers if prev_judge.parent else ""
            prev_judge.save()
            context['highlight_left_txt'] = left_response.highlight
            context['highlight_right_txt'] = right_response.highlight
        
        context['doc_left'] = left_response.document
        context['doc_right'] = right_response.document

        return (context, left_response, right_response)


    def post(self, request, *args, **kwargs):
        
        print("************************************************")
        print(self.request.path)
        print(self.request.body)
        print("************************************************")

        if 'prev' in request.POST: 
            return self.handle_prev_button(request.user, request.user.latest_judgment)

        elif 'left' in request.POST or 'right' in request.POST or 'equal' in request.POST:
            return self.handle_judgment_actions(request.user, request.user.latest_judgment, request.POST)
        
        elif 'done_back' in request.POST:
            prev_judge = request.user.latest_judgment
            prev_judge.is_round_done = False
            prev_judge.is_complete = False
            prev_judge.after_state = None
            prev_judge.task.is_completed = False
            prev_judge.task.best_answers = None
            prev_judge.task.save()
            prev_judge.save()

            return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {"user_id" : request.user.id, "judgment_id": prev_judge.id}
                )
            )


        return HttpResponseRedirect(reverse_lazy('core:home'))




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
                    'core:home' 
                )
            )

    
    def handle_judgment_actions(self, user, prev_judge, requested_action):
        """
        """
        action, after_state = JudgmentView.evaluate_after_state(requested_action, prev_judge.before_state)

        if prev_judge.is_tested:
            judgment = JudgmentView.handle_test_judgment(prev_judge, action)
            user.latest_judgment = judgment
            user.save()
            
            return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
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
                    'judgment:judgment', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )

        if prev_judge.is_round_done:
            logger.info(f'One round is finished! you are going to the next step!')

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
                'judgment:judgment', 
                kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
            )
        )
        else: 
            user.latest_judgment = judgement
            user.save()
            return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {"user_id" : user.id, "judgment_id": judgement.id}
                )
            )



    @staticmethod
    def get_fake_test_judgment(user, prev_judge):

        if settings.TREC_NAME != "deep_learning":
            return prev_judge, False

        is_test = False
        judgement_list = Judgment.objects.filter(
                task=prev_judge.task,
                has_changed=False,
                is_tested=False, 
            ).exclude(
                left_response=None,
            ).exclude(
                action=None,
            )

        
        # test when there is we meet next interval
        if len(judgement_list) < settings.JUDGMENT_TEST_INTERVAL or random.random() > 0.1:
            return prev_judge, is_test

        is_test = True
        
        tmp_judge = random.choice(judgement_list)
        tmp_judge.parent = prev_judge
        tmp_judge.best_answers = prev_judge.best_answers

        prev_judge = tmp_judge
        prev_judge.pk = None
        
        prev_judge.is_tested = True
        prev_judge.save()
        user.save()
        
        return prev_judge, is_test 
    

    @staticmethod
    def handle_test_judgment(prev_judge, action):
        

        is_consistent = False
        if prev_judge.action == action and action == 2:
            is_consistent = True

        if prev_judge.action == 3 and action == 1:
            is_consistent = True
        elif prev_judge.action == 1 and action == 3:
            is_consistent = True

        JudgmentConsistency.objects.create(
            task=prev_judge.task,
            judgment = prev_judge,
            is_consistent=is_consistent,
        )
        prev_judge.action = action
        prev_judge.save()
        judgment = Judgment.objects.filter(parent=prev_judge).first()
        return judgment

    @staticmethod   
    def evaluate_after_state(requested_action, before_state):
        """
        """
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


    @staticmethod
    def append_answer(state, judgment):
        best_docs = pref.get_best(state)
        answers = judgment.best_answers if judgment.best_answers else ""
        new_ans = ""
        for doc in best_docs:
            new_ans += doc + "|"
        return answers +"--"+new_ans

