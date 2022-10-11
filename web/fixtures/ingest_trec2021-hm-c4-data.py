import os
import pandas as pd
import html
from django.utils.html import strip_tags
from topic.models import Topic
from document.models import Document


ROOT_PATH =  "fixtures/trec2021-data"
print("1- Ingest topic")
ans = pd.read_csv(os.path.join(ROOT_PATH, 'questions.csv'), sep=" ", header=None)
for i, t in ans.iterrows():
    try:
        Topic.objects.create(uuid=t[0], title=t[1], description=t[2])
    except Exception as e:
        print(f"{t[0]} ==> {e}")


print("2- Ingest Document")
passages = pd.read_csv(os.path.join(ROOT_PATH, 'passages.csv'), header=None)
for i, t in passages.iterrows():
    
    try: 
        Document.objects.create(
            uuid = t[0],
            title = strip_tags(t[1]),
            url = strip_tags(t[2]),
            content = html.escape(strip_tags(t[3])) + "\n\n",
        )
    except Exception as e:
        print(e)

print("3- Map document to topics")
a_file = open(os.path.join(ROOT_PATH, "pool.csv"))
for line in a_file:
    topic_id, doc_id = line.split()
    try:
        document = Document.objects.get(uuid=doc_id)
        topic = Topic.objects.get(uuid=topic_id)
        document.topics.add(topic)
        document.save()
    except Exception as e:
        print(e)


print("4- Check if a topic has just one document!")
for topic in Topic.objects.all():
    document_list = Document.objects.filter(topics__uuid = topic.uuid)
    topic.num_related_document = len(document_list)
    topic.save()