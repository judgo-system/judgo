from django.db import models


from core.models import Session
from question.models import Question
from document.models import Documents
from web.settings import AUTH_USER_MODEL as User


class JudgingChoices(models.IntegerChoices):
    RIGHT = (1, 'Right')
    EQUAL = (0, 'Equal')
    LEFT = (-1, 'Left')

class Judgment(models.Model):
    class Meta:
        get_latest_by = "created_at"


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    # contain a pickle object of pref class
    state = models.BinaryField(verbose_name='State')

    # Indicate if it's the first judment by this user in this session for this question
    is_initialized = models.BooleanField(default=False)

    # Indicate if it's the judment on this question is finished or not.
    is_done = models.BooleanField(default=False)

    doc_left = models.ForeignKey(Documents, on_delete=models.CASCADE, 
                            related_name="left_document", null=True, blank=True)
    doc_right = models.ForeignKey(Documents, on_delete=models.CASCADE, 
                            related_name="right_docuemnt", null=True, blank=True)

        
    # This field uses for check which document is more relevant to the current question.
    # In fact, this action update the state field
    action = models.IntegerField(verbose_name='Action',
                                    choices=JudgingChoices.choices,
                                    null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


    def __str__(self):
        return "{} is judging question {}\n" \
        "the left docuemnt is {}\n" \
        " the right document is {} " \
        "the action made by user is {}".format(
            self.user, self.question, self.doc_left, 
            self.doc_right, self.action
        )