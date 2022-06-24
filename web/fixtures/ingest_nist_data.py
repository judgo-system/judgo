import json
import os
from inquiry.models import Question
from response.models import Document

# 1- prepare qrel file
topic_mappping = {}
with open('fixtures/nist_data/qrels.json', 'r') as f:
    data = json.load(f)
for topic, documents in data.items():
    # temp = []
    for doc, value in documents.items():
        if value !="0":
            # temp.append(doc)
            topic_mappping[doc] = topic
print(topic_mappping)


# 2= ingest topic
with open('fixtures/nist_data/topics.json', 'r') as f:
    data = json.load(f)
    for key, value in data.items():
        try:
            if key in topic_mappping.values():
                Question.objects.create(question_id=key, content=value['title'])
                print(f'{key}')

            # else: 
            #     print(f'there is no topic_mappping for topic id {key}')
        except:
            continue



# # 2- Ingest Document
doc_mappping = {}
path = 'fixtures/nist_data/docs'

for file in os.listdir(path):
    with open(os.path.join(path, file), 'r') as f:
        data = json.load(f)
        doc_mappping[data['pid']] = data['passage']

for doc, content in doc_mappping.items():
    if doc in topic_mappping:
        try:
            q = Question.objects.get(question_id=topic_mappping[doc])

            Document.objects.create(uuid=doc, content=" "+content, base_question=q)
        except:
            continue
            # print(f'question id {topic_mappping[doc]}')