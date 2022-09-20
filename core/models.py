from statistics import mode
from django.db import models
from web.settings import AUTH_USER_MODEL as User
from topic.models import Topic


class Task(models.Model):

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # user can have several keyword to highlight in documents
    tags = models.TextField(null=True, blank=True)

    # user can change the fond size of given document 
    font_size = models.TextField(null=True, blank=True)

    # number of best answer so far
    num_ans = models.IntegerField(default=0)

    # a list for saving best answer
    best_answers = models.TextField(null=True, blank=True)

    # if all answers are graded or not
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


    def __str__(self) -> str:
        return f'(User:{self.user.username}, Topic:{self.topic.title})'


