import pandas as pd
from topic.models import Topic
from document.models import Document


# 1= ingest question

ans = pd.read_csv('fixtures/question.csv')
for i, t in ans.iterrows():
    try:
        Topic.objects.create(uuid=t[0], title=t[1])
    except:
        continue


# 2- Ingest Document
d = {}
a_file = open("fixtures/pools.out")
for line in a_file:
    value, key = line.split()

    d[key] = value

p = pd.read_csv('fixtures/passages.csv')
for i, t in p.iterrows():
    if t[0] in d:

        q = Topic.objects.get(uuid=d[t[0]])
        try:
            Document.objects.create(uuid=t[0], content=" "+t[1], topic=q)
        except:
            continue