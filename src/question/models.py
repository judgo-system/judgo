from django.db import models


class Question(models.Model):

    question_id = models.CharField(max_length=50, unique=True)

    content = models.TextField(null=False)

    highlights = models.TextField(default="")
    
    def __str__(self):
        return f"{self.question_id} : {self.content}"