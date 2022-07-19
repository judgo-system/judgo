from django.db import models
from web.settings import AUTH_USER_MODEL as User
from topic.models import Topic


class Task(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)    

    # if step 1 which is to check if documents are usefull for topic or not is complete.
    usefulness_checked = models.BooleanField(default=False)
    
    # if step 2 which is to check if documents are support topic or not is complete.
    support_checked = models.BooleanField(default=False)
    
    # if step 3 which is to check if documents are support topic or not is complete.
    credibility_checked = models.BooleanField(default=False)
    
    # user can have several keyword to highlight in documents
    tags = models.TextField(null=True, blank=True)

    # number of best answer so far in step 3.
    num_ans = models.IntegerField(default=0)

    # a list for saving best answer in step3 
    best_answers = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)


    def __str__(self) -> str:
        return f'(User:{self.user.username}, Topic:{self.topic.title},\
            Step1: {self.usefulness_checked}, Step2: {self.support_checked}\
            Step3: {self.credibility_checked})'
