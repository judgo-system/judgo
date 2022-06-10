from xml.dom.minidom import Document
from django.db import models

from inquiry.models import Question
from core.models import Session

class Document(models.Model):

    uuid = models.CharField(max_length=100, unique=True)

    content = models.TextField()
    
    base_question = models.ForeignKey(
        Question, null=True, 
        on_delete=models.SET_NULL, related_name="base_question"
    )

    def __str__(self):
        return f"{self.uuid} : {self.content}"


# A table representing many-to-many relation between documents and session
class Response(models.Model):

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    # in each session, user can highlight several parts of documents
    highlight = models.TextField(null=True)
