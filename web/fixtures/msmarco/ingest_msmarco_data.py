import os
import pandas as pd
from topic.models import Topic
from document.models import Document

ROOT_PATH = os.path.join(os.getcwd(), "sample-data")

print("1- Ingest topic")
for i, t in pd.read_csv(os.path.join(ROOT_PATH, "question.csv")).iterrows():
    try:
        topic = Topic.objects.create(uuid=t[0], title=t[1])
    except Exception as e:
        print(f"{t[0]} ==> {e}")

# 2- Ingest Document
print("2- Map documents")
for i, t in pd.read_csv(os.path.join(ROOT_PATH, 'passages.csv')).iterrows():
    try:
        Document.objects.create(uuid=t[0], content=" "+t[1])
    except:
        continue

print("3- Map document to topics")
a_file = open(os.path.join(ROOT_PATH, "pools.out"))
for line in a_file:
    topic_id, doc_id = line.split()
    try:
        document = Document.objects.get(uuid=doc_id)
        topic = Topic.objects.get(uuid=topic_id)
        document.topics.add(topic)
        document.save()
    except Exception as e:
        continue
        # print(f"ERROR in line-{line} ==> {e}")


print("4- Check if a topic has just one document!")
for topic in Topic.objects.all():
    document_list = Document.objects.filter(topics__uuid = topic.uuid)
    topic.num_related_document = len(document_list)
    topic.save()