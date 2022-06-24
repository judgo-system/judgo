import pandas as pd
from inquiry.models import Question
from response.models import Document


# 1= ingest question

ans = pd.read_csv('fixtures/question.csv')
for i, t in ans.iterrows():
    try:
        Question.objects.create(question_id=t[0], content=t[1])
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

        q = Question.objects.get(question_id=d[t[0]])
        try:
            Document.objects.create(uuid=t[0], content=" "+t[1], base_question=q)
        except:
            continue