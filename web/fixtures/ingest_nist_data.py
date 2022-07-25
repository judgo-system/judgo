import json
import os
from topic.models import Topic
from document.models import Document

# 1- prepare qrel file
topic_mappping = {}
with open('fixtures/data/nist_data/qrels.json', 'r') as f:
    data = json.load(f)
for topic, documents in data.items():
    for doc, value in documents.items():
        if value !="0" and value !="1":
            topic_mappping[doc] = topic


# 2= ingest topic
with open('fixtures/data/nist_data/topics.json', 'r') as f:
    data = json.load(f)
    for key, value in data.items():
        try:
            if key in topic_mappping.values():
                Topic.objects.create(uuid=key, title=value['title'])
        except:
            continue



# # 2- Ingest Document
doc_mappping = {}
path = 'fixtures/data/nist_data/docs'

for file in os.listdir(path):
    with open(os.path.join(path, file), 'r') as f:
        data = json.load(f)
        doc_mappping[data['pid']] = data['passage']

for doc, content in doc_mappping.items():
    if doc in topic_mappping:
        try:
            topic = Topic.objects.get(uuid=topic_mappping[doc])

            Document.objects.create(uuid=doc, content=" "+content, topic=topic)
        except:
            continue
