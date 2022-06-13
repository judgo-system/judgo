import re
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
    pref_obj = None
    inquiry_id = None
    left_doc_id = None
    right_doc_id = None

    def render_to_response(self, context, **response_kwargs):
        "please don'w say you come here"
        response = super().render_to_response(context, **response_kwargs)
        response.set_cookie("inquiry_id", self.inquiry_id)
        response.set_cookie("left_doc_id", self.left_doc_id)
        response.set_cookie("right_doc_id", self.right_doc_id)

        return response

    def highlight_document(self, text, highlight):
        if not highlight:
            return text
        highlights = highlight.split("|||")

        for part in highlights:
            if part:
                text = text.replace(part, "<span class = 'highlight'>{}</span>".format(part))
        return text

    def get_context_data(self, **kwargs):
        
        context = super(JudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])
            
            # context['question_id'] = prev_judge.inquiry.question.question_id
            context['question_content'] = prev_judge.inquiry.question.content
            self.inquiry_id = prev_judge.inquiry.id
            

            if prev_judge.is_complete:
                context["is_finished"] = "complete"

                context["inquiry_question"] = prev_judge.inquiry.question.content

                context["best_answer_list"] = "\n\n".join(
                    x for x in prev_judge.inquiry.best_answers.split("|")
                )
            else:

                
                
                context['status'] = pref.get_str(prev_judge.before_state)
                
                print("current status: ")
                print(context['status'])


                (left, right) = pref.get_documents(prev_judge.before_state)
                context['left_id'] = left
                context['right_id'] = right

                left_doc = Document.objects.get(uuid=left)
                right_doc = Document.objects.get(uuid=right)
                left_response, _ = Response.objects.get_or_create(session= prev_judge.session, document=left_doc)
                right_response, _ = Response.objects.get_or_create(session= prev_judge.session, document=right_doc)

                if left_response.highlight :

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

                self.left_doc_id = left_response.id
                self.right_doc_id = right_response.id
                
                # if there is no tag is we don't need to fill it out.
                if prev_judge.inquiry.tags:
                    context['highlights'] = prev_judge.inquiry.tags

                    

        return context

    def get(self, request, *args, **kwargs):
        return super(JudgmentView, self).get(self, request, *args, **kwargs)



    def post(self, request, *args, **kwargs):
        
        
        user = User.objects.get(id=request.user.id)
        prev_judge = user.latest_judgment

        if 'prev' in request.POST: 
            return self.handle_prev_button(user, prev_judge)

        if 'left' in request.POST or 'right' in request.POST or 'equal' in request.POST:
            return self.handle_judgment_actions(user, prev_judge, request.POST)

        return HttpResponseRedirect(reverse_lazy('core:home'))

    
    def get_number_best_answer(self, judgment):
        count = 0
        temp = judgment
        while temp.is_initialized and temp.parent:
            count += 1
            temp = temp.parent
        return count


    def add_new_answer(self, state, inquiry):
        best_docs = pref.get_best(state)

        new_ans = inquiry.best_answers if inquiry.best_answers else "" 
        for doc in best_docs:
            if doc in new_ans:
                new_ans = new_ans.replace(f'{doc}|', '')
            new_ans += doc + "|"

        inquiry.best_answers = new_ans
        inquiry.save()

        return best_docs

    def handle_prev_button(self, user, prev_judge):

        if prev_judge.parent and not prev_judge.is_round_done:    
            user.latest_judgment = prev_judge.parent
            user.save()
            return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:judgment', 
                        kwargs = {"user_id" : user.id, "judgment_id": prev_judge.parent.id}
                    )
                )
        elif prev_judge.parent and  prev_judge.is_round_done:    
            user.latest_judgment = prev_judge.parent.parent
            user.save()
            return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:judgment', 
                        kwargs = {
                            "user_id" : user.id, 
                            "judgment_id": prev_judge.parent.parent.id
                        }
                    )
                )

        else:
            return HttpResponseRedirect(reverse_lazy('core:home'))

    
    def handle_judgment_actions(self, user, prev_judge, requested_action):
        
        # get documents 
        (left, right) = pref.get_documents(prev_judge.before_state)

        after_state = None
        action = None

        if 'left' in requested_action:
            action = JudgingChoices.LEFT
            after_state = pref.evaluate(prev_judge.before_state, left)
        elif 'right' in requested_action:
            action = JudgingChoices.RIGHT
            after_state = pref.evaluate(prev_judge.before_state, right)
        elif 'equal' in requested_action:
            action = JudgingChoices.EQUAL
            after_state = pref.evaluate(prev_judge.before_state, right, equal=True)
        
        if after_state:
        
            # the user is back to the same judment so we need to make a copy of this    
            if prev_judge.action != None:
                
                print(f"User change their mind about judment {prev_judge.id} which was {prev_judge.action}")
                prev_judge = Judgment.objects.create(
                    user=user,
                    session = user.active_session,
                    inquiry=prev_judge.inquiry,
                    before_state=prev_judge.before_state,
                    parent=prev_judge.parent
                )
                
            
            # update pre_judge action
            prev_judge.action = action
            prev_judge.after_state = after_state
            prev_judge.save()

            while pref.is_judgment_finished(after_state):

                answer = self.add_new_answer(after_state, prev_judge.inquiry)
                
                print(f'best answer so far: {answer}')

                prev_judge.is_round_done = True
                prev_judge.save() 
                after_state = pref.pop_best(after_state)
                
                prev_judge.after_state = after_state
                prev_judge.save()
            
            
                if pref.is_judgment_completed(after_state):
                    prev_judge.is_complete = True
                    prev_judge.inquiry.is_completed = True

                    prev_judge.inquiry.save()
                    prev_judge.save()
                    return HttpResponseRedirect(
                        reverse_lazy(
                            'inquiry:inquiry_complete', 
                            kwargs = {"user_id" : user.id, "inquiry_id": prev_judge.inquiry.id}
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
                    session = user.active_session,
                    inquiry=prev_judge.inquiry,
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
        


    