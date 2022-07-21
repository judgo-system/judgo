from django.db import models

from core.models import Task
from document.models import Response
from web.settings import AUTH_USER_MODEL as User


class PreferenceJudgmentChoices(models.IntegerChoices):
    RIGHT = (1, 'Right')
    EQUAL = (2, 'Equal')
    LEFT = (3, 'Left')

class RelevantJudgmentChoices(models.IntegerChoices):
    YES = (1, 'Yes')
    NO = (2, 'No')
    MAYBE = (3, 'Maybe')


class Judgment(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    # Indicate if it's the first judment by this user in this session for this question
    is_initialized = models.BooleanField(default=False)
    
    # Indicate if question judgment is completed which means we have
    #  all documents sorted in the best_answers.
    is_complete = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


    class Meta:
        abstract = True
        get_latest_by = "created_at"

    def __str__(self):
        return "(ID: {} USERNAME: {}, TOPIC: {}, )".format(self.pk,
            self.user.username, self.task.topic 
        )

class Step1Judgment(Judgment):


    # last judgmnet
    previous = models.ForeignKey(
        "self", blank=True, 
        null=True, on_delete=models.SET_NULL
    )

    # contain a pickle object of list of remaining document
    state = models.BinaryField(verbose_name='Before State')

    response = models.ForeignKey(
        Response, on_delete=models.CASCADE,
        null=True, blank=True
    )
        
    action = models.IntegerField(verbose_name='Action',
                                    choices=RelevantJudgmentChoices.choices,
                                    null=True, blank=True)

    def __str__(self):
        return "Step 1: " +super().__str__()


class Step2Judgment(Judgment):

    # last judgmnet
    previous = models.ForeignKey(
        "self", blank=True, 
        null=True, on_delete=models.SET_NULL
    )

    # contain a pickle object of list of remaining document
    state = models.BinaryField(verbose_name='Before State')

    response = models.ForeignKey(
        Response, on_delete=models.CASCADE,
        null=True, blank=True
    )
        
    action = models.IntegerField(verbose_name='Action',
                                    choices=RelevantJudgmentChoices.choices,
                                    null=True, blank=True)

    def __str__(self):
        return "Step 2: " +super().__str__()



class Step3Judgment(Judgment):

    # each judgment have a single parent which point to previos state of pref obj
    parent = models.ForeignKey(
        "self", blank=True, 
        null=True, on_delete=models.SET_NULL
    )


    # contain a pickle object of pref class before action
    before_state = models.BinaryField(verbose_name='Before State')

    # contain a pickle object of pref class after action
    after_state = models.BinaryField(verbose_name='After State')

    # Indicate if it's one round of  judment on this question is finished or not.
    is_round_done = models.BooleanField(default=False)

    left_response = models.ForeignKey(
        Response, on_delete=models.CASCADE, 
        related_name="left_response", null=True, blank=True
    )
    right_response = models.ForeignKey(
        Response, on_delete=models.CASCADE, 
        related_name="right_response", null=True, blank=True
    )

        
    # This field uses for check which document is more relevant to the current question.
    # In fact, this action update the state field
    action = models.IntegerField(verbose_name='Action',
                                    choices=PreferenceJudgmentChoices.choices,
                                    null=True, blank=True)
   
    def __str__(self):
        return "Step3: " + super().__str__()