from logging import RootLogger
import os
import pandas as pd
import html
from topic.models import Topic
from document.models import Document

ROOT_PATH =  "fixtures/data/trec_2021"
# 1= ingest question

ans = pd.read_csv(os.path.join(ROOT_PATH, 'questions.csv'), sep=" ")
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
            # content = html.escape(t[3])
            
            Document.objects.create(
                uuid=t[0], 
                title=html.escape(t[1]),
                url=html.escape(t[2]),
                content=" "+ html.escape(t[3]).replace("\n\n", "\n"), 
                topic=q)
        except Exception as e:
            print(e)
            continue