import re
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from response.models import Document, Response
from judgment.models import Judgment, JudgingChoices
from user.models import User
from interfaces import pref
# from web.judgment.templatetags.highlight_keywords import highlight_search

class JudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'judgment.html'
    pref_obj = None
    

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
        highlights = highlight.split(",")[:-1]
        
        for part in highlights:
            highlighted = re.sub(
                part, 
                "<span class = 'highlight'>{}</span>".format(part), 
                text, 
                flags=re.IGNORECASE)
            text = highlighted
        return text

    def get_context_data(self, **kwargs):
        
        context = super(JudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            # get the latest judment for this user and question
            prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])

            (left, right) = pref.get_documents(prev_judge.state)
            context['question_id'] = prev_judge.inquiry.question.question_id
            context['question_content'] = prev_judge.inquiry.question.content
            context['status'] = pref.get_str(prev_judge.state)

            context['left_id'] = left
            context['right_id'] = right

            left_doc = Document.objects.get(uuid=left)
            right_doc = Document.objects.get(uuid=right)
            left_response, _ = Response.objects.get_or_create(session= prev_judge.session, document=left_doc)
            right_response, _ = Response.objects.get_or_create(session= prev_judge.session, document=right_doc)

            if left_response.highlight :
                print("left one")
                print(left_response.highlight)
                context['left_txt'] = self.highlight_document(
                    left_response.document.content,
                    left_response.highlight
                ) 
            else:
                context['left_txt'] = left_response.document.content
            
            if right_response.highlight:
                print('right one')
                print(right_response.highlight)
                context['right_txt'] = self.highlight_document(
                    right_response.document.content,
                    right_response.highlight
                ) 
            else:
                context['right_txt'] = right_response.document.content

            self.left_doc_id = left_response.id
            self.right_doc_id = right_response.id
            self.inquiry_id = prev_judge.inquiry.id
            
            # if there is no tag is we don't need to fill it out.
            if prev_judge.inquiry.tags:
                context['highlights'] = prev_judge.inquiry.tags
                
        return context

    def get(self, request, *args, **kwargs):
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            prev_judge = Judgment.objects.get(id=self.kwargs['judgment_id'])

            if pref.is_finish(prev_judge.state):
                return HttpResponseRedirect(reverse_lazy('core:home'))
        return super(JudgmentView, self).get(self, request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        
        user = User.objects.get(id=request.user.id)
        prev_judge = user.latest_judgment

        if 'prev' in request.POST: 
            return self.handle_prev_button(user, prev_judge)

        if 'left' in request.POST or 'right' in request.POST or 'equal' in request.POST:
            return self.handle_judgment_actions(user, prev_judge, request.POST)

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
        else:
            return HttpResponseRedirect(reverse_lazy('core:home'))

    
    def handle_judgment_actions(self, user, prev_judge, requested_action):
        
        # get documents 
        (left, right) = pref.get_documents(prev_judge.state)

        state = None
        action = None

        if 'left' in requested_action:
            action = JudgingChoices.LEFT
            state = pref.evaluate(prev_judge.state, left)
        elif 'right' in requested_action:
            action = JudgingChoices.RIGHT
            state = pref.evaluate(prev_judge.state, right)
        elif 'equal' in requested_action:
            action = JudgingChoices.EQUAL
            state = pref.evaluate(prev_judge.state, right, equal=True)
        
        if state:
        
            left_doc = Document.objects.get(uuid=left)
            right_doc = Document.objects.get(uuid=right)
            left_response, _ = Response.objects.get_or_create(session= prev_judge.session, document=left_doc)
            right_response, _ = Response.objects.get_or_create(session= prev_judge.session, document=right_doc)

            judgement = Judgment.objects.create(
                    user=user,
                    session = user.active_session,
                    inquiry=prev_judge.inquiry,
                    state=state,
                    action=action,
                    left_response=left_response,
                    right_response=right_response,
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
        

    