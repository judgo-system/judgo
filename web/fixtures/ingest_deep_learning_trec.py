import json
import os
from topic.models import Topic
from document.models import Document



# 1- prepare qrel file
topic_mappping = {}
with open('fixtures/data/deep_learning/qrels.json', 'r') as f:
    data = json.load(f)
for topic, documents in data.items():
    for doc, value in documents.items():
        if value !="0" and value !="1":
            topic_mappping[doc] = topic

# print(topic_mappping)
# 1= ingest topic
print("1-Ingest Topics")
with open('fixtures/data/deep_learning/topics.json', 'r') as f:
    data = json.load(f)
    for key, value in data.items():
        try:
            if key in topic_mappping.values():
                Topic.objects.create(uuid=key, title=value['title'])
        except Exception as e:
            print(e)
            



# # 2- Ingest Document
path = 'fixtures/data/deep_learning/docs'
print("2-Ingest Documents")
for file in os.listdir(path):
    with open(os.path.join(path, file), 'r') as f:
        data = json.load(f)
        try:
            if data['pid'] in topic_mappping:
                Document.objects.create(uuid=data['pid'], content=" "+data['passage'], url=data['pid'])
        except Exception as e:
            print(e)


print("3- Map document to topics")
for doc, topic in topic_mappping.items():
    try:
        document = Document.objects.get(uuid=doc)
        topic = Topic.objects.get(uuid=topic)
        document.topics.add(topic)
        document.save()
    except Exception as e:
        print(e)


print("4- Check if a topic has just one document!")
for topic in Topic.objects.all():
    document_list = Document.objects.filter(topics__uuid = topic.uuid)
    topic.num_related_document = len(document_list)
    topic.save()
            
