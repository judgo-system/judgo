from datetime import datetime
from django.db import models
from web.settings import AUTH_USER_MODEL as User
from topic.models import Topic


class Task(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)    

    # if step 1 which is to check if documents are usefull for topic or not is complete.
    step1_checked = models.BooleanField(default=False)
    
    # if step 2 which is to check if documents are support topic or not is complete.
    step2_checked = models.BooleanField(default=False)
    
    # if step 3 which is judge documents is complete.
    step3_checked = models.BooleanField(default=False)
    
    # user can have several keyword to highlight in documents
    tags = models.TextField(null=True, blank=True)

    num_doc_step1 = models.IntegerField(default=0)
    
    num_doc_step2 = models.IntegerField(default=0)
    
    # number of best answer so far in step 3.
    num_ans = models.IntegerField(default=0)

    # a list for saving best answer in step3 
    best_answers = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    
    updated_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self) -> str:
        return f'(User:{self.user.username}, Topic:{self.topic.title},\
            Step1: {self.step1_checked}, Step2: {self.step2_checked}\
            Step3: {self.step3_checked})'



    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)