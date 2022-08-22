import html
from pathlib import Path

from core.models import Task
from django.utils.html import strip_tags
from document.models import Document
from topic.models import Topic
from user.models import User

ROOT_PATH = "fixtures/data/test"
Path(ROOT_PATH).mkdir(exist_ok=True, parents=True)
import pandas as pd

df = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/1siwC0S1vgs_BB9lQC6z7J1smTDFA3P0oJMfcSy7DYME/export?gid=0&format=csv",
)

questions = df[["scenario"]].apply(lambda row: pd.Series([row.name, row.scenario, row.scenario]), axis=1).sample(frac=1)
passages = (
    df.input.apply(lambda x: x.split())
        .explode().drop_duplicates().apply(lambda x: pd.Series([x, x, x, x], index="uuid title url content".split()))
).sample(frac=1)
pool = (
    df.input.apply(lambda x: x.split())
        .explode()
        .reset_index()
        .rename(columns=dict(index="topic"))
        .apply(lambda x: pd.Series([x.topic, x.input]), axis=1)
).sample(frac=1)
Topic.objects.all().delete()
Document.objects.all().delete()
Task.objects.all().delete()
User.objects.filter(username="test_user").delete()
user = User.objects.create_user(username="test_user", password="test_user@example.com", email="test_user@example.com")

print("1- Ingest topic")
for i, t in questions.iterrows():
    try:
        Topic.objects.create(uuid=t[0], title=t[1], description=t[2])
    except Exception as e:
        print(f"{t[0]} ==> {e}")

print("2- Ingest Document")
for i, t in passages.iterrows():
    try:
        Document.objects.create(
            uuid=t[0],
            title=strip_tags(t[1]),
            url=strip_tags(t[2]),
            content=html.escape(strip_tags(t[3])) + "\n\n",
        )
    except Exception as e:
        print(e)

print("3- Map document to topics")
for line in pool.itertuples():
    _, topic_id, doc_id = line
    try:
        document = Document.objects.get(uuid=doc_id)
        topic = Topic.objects.get(uuid=topic_id)
        document.topics.add(topic)
        document.save()
    except Exception as e:
        print(e)

print("4- Check if a topic has just one document!")
for topic in Topic.objects.all():
    document_list = Document.objects.filter(topics__uuid=topic.uuid)
    topic.num_related_document = len(document_list)
    topic.save()

for topic in Topic.objects.all():
    Task.objects.create(
        user_id=user.id,
        topic_id=topic.id
    )
