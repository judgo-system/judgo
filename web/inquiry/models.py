from django.db import models


class Question(models.Model):
    
    question_id = models.CharField(max_length=50, unique=True)

    content = models.TextField(null=False)

    def __str__(self):
        return f"{self.id}: ({self.question_id}, {self.content})"