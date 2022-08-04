from xml.dom.minidom import Document
from django.db import models

from topic.models import Topic
from web.settings import AUTH_USER_MODEL as User

class Document(models.Model):

    uuid = models.CharField(max_length=100, unique=True)

    content = models.TextField()
    
    title = models.TextField()

    url = models.TextField()
    

    topics = models.ManyToManyField(
        Topic, 
        related_name="topics"
    )

    def __str__(self):
        return f"{self.uuid} : ({self.title}, {self.url})"


# A table representing many-to-many relation between documents and session
class Response(models.Model):

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Each user, user can highlight several parts of documents
    highlight = models.TextField(null=True)


    def __str__(self):
        return f"{self.document.uuid}"