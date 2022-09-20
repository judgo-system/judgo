from django.db import models


class Topic(models.Model):
    
    uuid = models.CharField(max_length=50, unique=True)

    title = models.TextField(null=False)

    description = models.TextField(null=False)

    num_related_document = models.IntegerField(default=0)
    
    def __str__(self):
        return f"({self.uuid}, {self.num_related_document}, {self.title})"


    def represent(self):
        return f'{self.title} ({self.uuid.split("_")[1].upper()})'
