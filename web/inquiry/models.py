from django.db import models

from core.models import Session

class Question(models.Model):
    
    question_id = models.CharField(max_length=50, unique=True)

    content = models.TextField(null=False)

    def __str__(self):
        return f"{self.question_id} : {self.content}"


# A table representing many-to-many relation between question and session
class Inquiry(models.Model):

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    # in each session, user can have several keyword to highlight in documents
    tags = models.TextField(null=True)

    # a list for saving best answer
    best_answers = models.TextField(null=True)

    # if all answers are graded or not
    is_completed = models.BooleanField(default=False)




