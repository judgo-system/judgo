from logging import RootLogger
import os
from pydoc import doc
import pandas as pd
import html
from topic.models import Topic
from core.models import Task
from document.models import Document
from user.models import User

ROOT_PATH =  "fixtures/data/trec_2021"
# 1= ingest question

ans = pd.read_csv(os.path.join(ROOT_PATH, 'questions.csv'), sep=" ", header=None)
for i, t in ans.iterrows():
    try:
        Topic.objects.create(uuid=t[0], title=t[1], description=t[2])
    except Exception as e:
        print(f"{t[0]} ==> {e}")


# 2- Ingest Document
d = {}
a_file = open(os.path.join(ROOT_PATH, "pool.out"))
for line in a_file:
    value, key = line.split()
    d[key] = value

p = pd.read_csv(os.path.join(ROOT_PATH, 'trec2021_subset_c4_passages.csv'))
for i, t in p.iterrows():
    if t[0] in d:

        q = Topic.objects.get(uuid=d[t[0]])
        try:
            
            Document.objects.create(
                uuid=t[0], 
                title=html.escape(t[1]),
                url=html.escape(t[2]),
                content=" "+ html.escape(t[3]).replace("\n\n", "\n"), 
                topic=q)
        except Exception as e:
            print(e)
            continue



## check if a topic has just one document!
for topic in Topic.objects.all():
    document_list = Document.objects.filter(topic__uuid = topic.uuid)
    topic.num_related_document = len(document_list)
    topic.save()


