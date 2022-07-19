from django.db import models


class Topic(models.Model):
    
    uuid = models.CharField(max_length=50, unique=True)

    title = models.TextField(null=False)

    def __str__(self):
        return f"({self.uuid}, {self.title})"