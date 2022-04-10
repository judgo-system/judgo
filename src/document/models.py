from django.db import models

from question.models import Question

# Create your models here.
class Documents(models.Model):

    uuid = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    base_question = models.ForeignKey(Question, null=True, on_delete=models.SET_NULL, related_name="base_question")

    def __str__(self):
        return f"{self.uuid} : {self.content}"