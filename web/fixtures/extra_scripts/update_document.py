import os
import pandas as pd
import html
from django.utils.html import strip_tags
from topic.models import Topic
from document.models import Document


ROOT_PATH =  "fixtures/data/trec_2021"


print("2- Update Document")
passages = pd.read_csv(os.path.join(ROOT_PATH, 'trec2021_subset_c4_passages.csv'))
for i, t in passages.iterrows(): 
    try: 
        document = Document.objects.get( uuid = t[0])
        document.title = strip_tags(t[1])
        document.url = strip_tags(t[2])
        document.content = html.escape(strip_tags(t[3])) + "\n\n"
        
    except Exception as e:
        print(e)