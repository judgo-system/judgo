from django.db import models

from core.models import Session
from inquiry.models import Inquiry
from response.models import Response
from web.settings import AUTH_USER_MODEL as User


class JudgingChoices(models.IntegerChoices):
    RIGHT = (1, 'Right')
    EQUAL = (0, 'Equal')
    LEFT = (-1, 'Left')


class Judgment(models.Model):
    class Meta:
        get_latest_by = "created_at"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    
    # each judgment have a single parent which point to previos state of pref obj
    parent = models.ForeignKey(
        "self", blank=True, 
        null=True, on_delete=models.SET_NULL
    )

    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE)


    # contain a pickle object of pref class before action
    before_state = models.BinaryField(verbose_name='Before State')

    # contain a pickle object of pref class after action
    after_state = models.BinaryField(verbose_name='After State')


    # Indicate if it's the first judment by this user in this session for this question
    is_initialized = models.BooleanField(default=False)

    # Indicate if it's one round of  judment on this question is finished or not.
    is_round_done = models.BooleanField(default=False)

    # Indicate if question judgment is completed which means we have
    #  all documents sorted in the best_answers.
    is_complete = models.BooleanField(default=False)

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
                                    choices=JudgingChoices.choices,
                                    null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now_add=True, editable=False)



    def __str__(self):
        return "{} is judging question {}\n" \
        "the left docuemnt is {}\n" \
        " the right document is {} " \
        "the action made by user is {}".format(
            self.user, self.inquiry, self.left_reponse, 
            self.right_reponse, self.action
        )