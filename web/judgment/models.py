from django.db import models

from core.models import Task
from document.models import Response
from web.settings import AUTH_USER_MODEL as User


class JudgingChoices(models.IntegerChoices):
    RIGHT = (1, 'Right')
    EQUAL = (2, 'Equal')
    LEFT = (3, 'Left')


class Judgment(models.Model):
    class Meta:
        get_latest_by = "created_at"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # each judgment have a single parent which point to previos state of pref obj
    parent = models.ForeignKey(
        "self", blank=True, 
        null=True, on_delete=models.SET_NULL
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE)


    # contain a pickle object of pref class before action
    before_state = models.BinaryField(verbose_name='Before State')

    # contain a pickle object of pref class after action
    after_state = models.BinaryField(verbose_name='After State')


    # # Indicate if it's the first judment by this user in this session for this question
    # is_initialized = models.BooleanField(default=False)

    # Indicate if it's one round of  judment on this question is finished or not.
    is_round_done = models.BooleanField(default=False)

    # Indicate if question judgment is completed which means we have
    #  all documents sorted in the best_answers.
    is_complete = models.BooleanField(default=False)

    # Indicate if user decided to change this or not!
    has_changed = models.BooleanField(default=False)

    # Indicate if this judgment is used for test or not!
    is_tested = models.BooleanField(default=False)    

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
    
    best_answers = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)



    def __str__(self):
        if self.left_response and self.right_response:
            return "(USERNAME: {}, QUESTION{}, LEFT RESPONSE: {}, RIGHT RESPONSE: {})".format(
                self.user.username, self.task.topic, self.left_response.document, self.right_response.document
            )            
        return "(ID: {} USERNAME: {}, Topic{})".format(self.pk,
            self.user.username, self.task.topic
        )


class JudgmentConsistency(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    judgment = models.ForeignKey(Judgment, on_delete=models.CASCADE)

    previous_action = models.CharField(max_length=10)
    
    current_action =  models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self) -> str:
        return f'(User:{self.user.username}, \
            Topic:{self.task.topic.title}, \
            Judgment:{self.judgment.id}, \
            Previous Action: {self.previous_action} \
            Current Action: {self.current_action})'
