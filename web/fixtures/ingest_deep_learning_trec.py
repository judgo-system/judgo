import collections
from gc import collect
import json
import os
from topic.models import Topic
from document.models import Document


# 1- prepare qrel file
topic_mappping = {}
with open('fixtures/data/deep_learning/qrels.json', 'r') as f:
    data = json.load(f)
for topic, documents in data.items():
    docs_list = [[] for i in range(4)]
    for doc, value in documents.items():
        docs_list[int(value)].append(doc)
    
    count = 0
    
    for i in range(len(docs_list)-1, -1, -1):
        docs = docs_list[i]
        if count >= 20:
            break
        for d in docs:
            topic_mappping[d] = topic
        count += len(docs)
    print(f"{topic} ==> {count}")
    

# 2= ingest topic
print("1-Ingest Topics")
with open('fixtures/data/deep_learning/topics.json', 'r') as f:
    data = json.load(f)
    for key, value in data.items():
        try:
            if key in topic_mappping.values():
                Topic.objects.create(uuid=key, title=value['title'])
        except Exception as e:
            print(e)
            



# 3- Ingest Document
path = 'fixtures/data/deep_learning/docs'
print("2-Ingest Documents")
for file in os.listdir(path):
    with open(os.path.join(path, file), 'r') as f:
        data = json.load(f)
        try:
            if data['pid'] in topic_mappping:
                Document.objects.create(uuid=data['pid'], content=" "+data['passage'], url="#")
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
            
