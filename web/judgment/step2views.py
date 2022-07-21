from asyncio import tasks
import logging
import pickle
from braces.views import LoginRequiredMixin

from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from document.models import Document, Response
from core.models import Task
from . import helper
from interfaces import pref
from .models import RelevantJudgmentChoices, Step2Judgment, Step3Judgment


logger = logging.getLogger(__name__)


class Step2JudgmentView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'single_judgment.html'
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

        return response


    def get_context_data(self, **kwargs):
        
        context = super(Step2JudgmentView, self).get_context_data(**kwargs)
        
        if "judgment_id" in kwargs and 'user_id' in kwargs:
            
            prev_judge = Step2Judgment.objects.get(id=self.kwargs['judgment_id'])
            
            context["judgment_id"] = self.kwargs['judgment_id']
            context["task_id"] = prev_judge.task.id
            context["step_name"] = "STEP 2 "
            
            
            if prev_judge.is_complete:
                context["task_status"] = "complete"
                return context

            self.task_id = prev_judge.task.id
            context['question'] = "Is this document is credible for this topic?"

            context['question_content'] = prev_judge.task.topic.title
            doc_list = pickle.loads(prev_judge.state)
            doc_id = doc_list[-1]
            context["progress_bar_width"] = round(
                100 * (1 -len(doc_list) / prev_judge.task.num_doc_step2),
                2
            )
            

            context['document_id'] = doc_id
            doc = Document.objects.get(uuid=doc_id)
            response, _ = Response.objects.get_or_create(user=self.request.user, document=doc)
            prev_judge.response = response
            prev_judge.save()

            self.left_doc_id = response.id

            if response.highlight:
                context['document_txt'] = helper.highlight_document(
                    response.document.content,
                    response.highlight
                ) 
            else:
                context['document_txt'] = response.document.content

                
            # if there is no tag is we don't need to fill it out.
            if prev_judge.task.tags:
                context['highlights'] = prev_judge.task.tags
        
        return context


    def post(self, request, *args, **kwargs):
        
        if 'prev' in request.POST: 
            judgment = Step2Judgment.objects.get(id=request.POST["prev"])
            return self.handle_prev_button(request.user, judgment)

        elif 'yes' in request.POST:
            action = RelevantJudgmentChoices.YES
            judgment = Step2Judgment.objects.get(id=request.POST["yes"])
            return self.handle_judgment_actions(request.user, judgment, action)
        elif 'no' in request.POST:
            action = RelevantJudgmentChoices.NO
            judgment = Step2Judgment.objects.get(id=request.POST["no"])
            return self.handle_judgment_actions(request.user, judgment, action)        
        elif 'maybe' in request.POST:
            action = RelevantJudgmentChoices.MAYBE
            judgment = Step2Judgment.objects.get(id=request.POST["maybe"])
            return self.handle_judgment_actions(request.user, judgment, action) 
        elif 'next_step' in request.POST:
            task = Task.objects.get(id=request.POST["next_step"])
            return self.setup_step3(request.user, task)

        return HttpResponseRedirect(reverse_lazy('core:home'))




    def handle_prev_button(self, user, prev_judge):

        if prev_judge.previous:    
            # user.latest_step2_judgment = prev_judge.previous
            user.save()
            return HttpResponseRedirect(
                    reverse_lazy(
                        'judgment:step2', 
                        kwargs = {"user_id" : user.id, "judgment_id": prev_judge.previous.id}
                    )
                )

        return HttpResponseRedirect(
                reverse_lazy(
                    'core:home' 
                )
            )


    def handle_judgment_actions(self, user, prev_judge, action):
        """
        """
        
        # the user is back to the same judment so we need to make a copy of this    
        if prev_judge.action != None:
            logger.info(f"User change their mind about judment {prev_judge.id} which was {prev_judge.action}")
        
        #update pre_judge action
        prev_judge.action = action
        prev_judge.save()
        
        doc_list = pickle.loads(prev_judge.state)
        
        doc_list.pop()

        if doc_list:
            judgement = Step2Judgment.objects.create(
                user=user,
                task=prev_judge.task,
                state=pickle.dumps(doc_list),
                previous=prev_judge
                )

            # user.latest_Step2_judgment = judgement
            user.save()
            return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:step2', 
                    kwargs = {"user_id" : user.id, "judgment_id": judgement.id}
                )
            )

        # Step2 is complete now
        
        prev_judge.is_complete = True
        prev_judge.task.step2_checked = True

        prev_judge.task.save()
        prev_judge.save()
        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:step2', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )

    def setup_step3(self, user, task):
        
        documents = list(Step2Judgment.objects.filter(
                user=self.request.user.id,
                task=task.id,
                action=RelevantJudgmentChoices.YES
            ).values_list('response__document__uuid', flat=True))
        state = pref.create_new_pref_obj(documents)


        
        prev_judge = Step3Judgment.objects.create(
                user=self.request.user,
                task=task,
                before_state=state,
            )
        user.latest_judgment = prev_judge
        user.save()

        return HttpResponseRedirect(
                reverse_lazy(
                    'judgment:step3', 
                    kwargs = {"user_id" : user.id, "judgment_id": prev_judge.id}
                )
            )
  