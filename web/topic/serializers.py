from rest_framework import serializers
from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'question', 'session', 'tags', 'best_answers')