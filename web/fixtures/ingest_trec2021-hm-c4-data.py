import pandas as pd
import html
from topic.models import Topic
from document.models import Document


# 1= ingest question

ans = pd.read_csv('fixtures/trec2021-hm-c4-questions.csv')
for i, t in ans.iterrows():
    try:
        Topic.objects.create(uuid=t[0], title=t[1])
    except Exception as e:
        print(f"{t[0]} ==> {e}")


# 2- Ingest Document
d = {}
a_file = open("fixtures/trec2021-hm-c4-pools.out")
for line in a_file:
    value, key = line.split()
    d[key] = value

p = pd.read_csv('fixtures/trec2021-hm-c4-passages.csv')
for i, t in p.iterrows():
    if t[0] in d:

        q = Topic.objects.get(uuid=d[t[0]])
        try:
            content = html.escape(t[1])
            Document.objects.create(uuid=t[0], content=" "+ content, topic=q)
        except Exception as e:
            print(e)
            continue