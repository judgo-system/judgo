from ast import literal_eval
import html
# import logging
from tracemalloc import start
from operator import itemgetter
from datetime import datetime

from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from document.models import Document, Response
from judgment.models import Judgment, JudgingChoices
from interfaces import pref, add_log

# logger = logging.getLogger(__name__)

class JudgmentView(LoginRequiredMixin, generic.TemplateView):
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
        
        context = super(JudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])

            if prev_judge.is_complete:
                context["task_status"] = "complete"
                return context

            self.task_id = prev_judge.task.id
            (left, right) = pref.get_documents(prev_judge.before_state)
            
            context['topic'] = prev_judge.task.topic
            context['font_size'] = prev_judge.task.font_size

            context["progress_bar_width"] = pref.get_progress_count(prev_judge.before_state)
            
            context['state_object'] = pref.get_str(prev_judge.before_state)
            

            left_doc = Document.objects.get(uuid=left, topics=prev_judge.task.topic)
            right_doc = Document.objects.get(uuid=right, topics=prev_judge.task.topic)
            left_response, _ = Response.objects.get_or_create(user=self.request.user, document=left_doc)
            right_response, _ = Response.objects.get_or_create(user=self.request.user, document=right_doc)


            context['doc_left'] = left_response.document
            context['doc_right'] = right_response.document

            prev_judge.left_response = left_response
            prev_judge.right_response = right_response
            # prev_judge.best_answers = prev_judge.parent.best_answers if prev_judge.parent else ""

            prev_judge.save()

            self.left_doc_id = left_response.id
            self.right_doc_id = right_response.id

            # if left_response.highlight:
            context['highlight_left_txt'] = left_response.highlight 
            # else:
            context['left_txt'] = f"Title: {left_response.document.title}"\
                    f"\nDocument ID: {left_response.document.uuid}\n\n"\
                    f"{left_response.document.content}"
                
            # if right_response.highlight:
            context['highlight_right_txt'] = right_response.highlight
            # else:
            context['right_txt'] = f"Title: {right_response.document.title}"\
                    f"\nDocument ID: {right_response.document.uuid}\n\n"\
                    f"{right_response.document.content}"



            # if there is no tag is we don't need to fill it out.
            if prev_judge.task.tags:
                # modifyed tag inorder to work according Tagify information
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

        # the user is back to the same judgment so we need to make a copy of this 
        if prev_judge.action != None:
            add_log.add_log_entry(user, f"The user = '{user.username}' changed their mind about judgement {prev_judge.id} which was '{prev_judge.action}' for topic_id = '{prev_judge.task.topic.uuid}', topic_title = '{prev_judge.task.topic.title}")
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
            
        # update pre_judge action
        prev_judge.action = action
        prev_judge.completed_at = datetime.now()
        prev_judge.after_state = after_state
        prev_judge.save()

        # logger.info(f"For topic_id = '{prev_judge.task.topic.uuid}' with topic_title = '{prev_judge.task.topic.title}', the user = '{user.username}' began judgement id {prev_judge.id} at {prev_judge.created_at}")
        # logger.info(f"For topic_id = '{prev_judge.task.topic.uuid}' with topic_title = '{prev_judge.task.topic.title}', the user = '{user.username}' completed action: '{prev_judge.action.label}' for judgement id {prev_judge.id} at {prev_judge.completed_at}")
        add_log.add_log_entry(user, f"User = '{user.username}' began judgement id {prev_judge.id} at {prev_judge.created_at} for topic_id = '{prev_judge.task.topic.uuid}', topic_title = '{prev_judge.task.topic.title}")
        add_log.add_log_entry(user, f"User = '{user.username}' completed action: '{prev_judge.action.label}' for judgement id {prev_judge.id} at {prev_judge.completed_at} for topic_id = '{prev_judge.task.topic.uuid}', topic_title = '{prev_judge.task.topic.title}")

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
                prev_judge.is_complete = True
                prev_judge.task.is_completed = True
                prev_judge.task.best_answers = prev_judge.best_answers
                prev_judge.task.save()
                prev_judge.save()

                # logger.info(f"User = '{user.username}' has completed judging topic_id = '{prev_judge.task.topic.uuid}', topic_title = '{prev_judge.task.topic.title}'!")
                add_log.add_log_entry(user, f"User = '{user.username}' has completed judging topic_id = '{prev_judge.task.topic.uuid}', topic_title = '{prev_judge.task.topic.title}'!")

                return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:judgment', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )

        # if prev_judge.is_round_done:
        #     logger.info(f'One round is finished! You are going to the next step!')

        judgement = Judgment.objects.create(
                user=user,
                task=prev_judge.task,
                before_state=after_state,
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


    # @staticmethod 
    # def highlight_document(text, highlight):
    #     """
    #     """
        # text = highlight
        # if not highlight:
        #     return text

        # highlights = highlight.split("|||")
        # sorted_list = []
        # for i, part in enumerate(highlights):
        #     span = "|".join([i for i in part.split("|")[:-1]])
        #     if len(span) < 3:
        #         continue
        #     startpoint, endpoint = part[len(span)+1:].split("-")
        #     startpoint, endpoint = int(startpoint), int(endpoint)

        #     sorted_list.append((startpoint, endpoint, span))

        # highlights = sorted(sorted_list, key=itemgetter(0))
        # offset = 0
        # for startpoint, endpoint, highlight  in highlights:
            
        #     startpoint = startpoint + offset
        #     endpoint = endpoint + offset
        
        #     html_tag = f"<span class = 'highlight' value={startpoint}-{endpoint}>"
        #     offset += len(html_tag) + len("</span>")
        #     text = text[:startpoint-1] + html_tag + highlight + "</span>" + text[endpoint-1:]
        #     # text = text.replace(highlighted_part,
        #     #  "<span class = 'highlight' value={}>{}</span>".format(f"{startpoint}-{endpoint}", highlighted_part))
        # return highlight

    @staticmethod
    def append_answer(state, judgment):
        best_docs = pref.get_best(state)
        answers = judgment.best_answers if judgment.best_answers else ""
        new_ans = ""
        for doc in best_docs:
            new_ans += doc + "|"
        return answers +"--"+new_ans


