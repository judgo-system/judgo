# -*- coding: utf-8 -*-
"""
@author: LinhNhiPM

"""

import pandas as pd
import xml.etree.cElementTree as et
import numpy as np


## Paths
topics_path = '/Users/lnphanmi/Desktop/Thesis/trec2022/trec2022-pref-judge-conversion/input/misinfo-2022-topics-with-answers.xml'
qrels_path = '/Users/lnphanmi/Desktop/Thesis/trec2022/trec2022-pref-judge-conversion/input/qrels.173'
save_path = '/Users/lnphanmi/Desktop/Thesis/trec2022/trec2022-pref-judge-conversion/output'

## trec2022 topic_ids 151 to 200
#topic_ids = [151, 152, 155, 159, 164, 167] ~ first set of 6 topics
#topic_ids = [155] ~ running revised 155 qrels
topic_ids = [173] 

## threshold = k
threshold = 10

if __name__ == '__main__':
    print('[1] Reading from the topics file ...')
    topics_head = ['topic_id', 'query', 'question', 'background', 'disclaimer', 'topic_answer', 'evidence']
    xml_root = et.parse(topics_path)
    rows = xml_root.findall('topic')

    xml_data = [[int(row.find('number').text), row.find('query').text, row.find('question').text, row.find('background').text,
                  row.find('disclaimer').text, row.find('answer').text, row.find('evidence').text] for row in rows]

    topics = pd.DataFrame(xml_data, columns=topics_head)
    
    
    print('[2] Reading qrels files...')
    qrel = pd.read_csv(qrels_path, header=None, sep=' ',
                       names=['topic_id', 'doc_no', 'usefulness', 'answer'],
                       dtype={'topic_id' : np.int64})
    
    
    print('[3] Creating questions file...')
    questions = topics[topics['topic_id'].isin(topic_ids)]
    
    for i, row in questions.iterrows():            
        questions.at[i, 'question'] = questions['question'][i] + ' (Answer is ' + questions['topic_answer'][i] + ')'
    
    final_questions = questions[['topic_id', 'question', 'background']]
    final_questions.to_csv(save_path + '/questions.csv', index=False, header=False, sep=' ')
    
    
    print('[4] Creating pools file...')
    topics_truncated = topics[['topic_id' , 'topic_answer']]
    filtered_qrel = qrel.loc[qrel['usefulness'].isin([1,2])]
    filtered_qrel = filtered_qrel.loc[qrel['answer'].isin([0,1,2])]
    filtered_qrel = pd.merge(filtered_qrel, topics_truncated, how='left', on='topic_id')

    final_df = pd.DataFrame(columns=['topic_id', 'doc_no', 'usefulness', 'answer', 'topic_answer'])
    for topic in topic_ids:
        df = filtered_qrel.loc[filtered_qrel['topic_id'] == topic]

        # All correct documents
        docs = df.loc[((df['topic_answer'] == 'Yes') & (df['answer'] == 1)) | ((df['topic_answer'] == 'No') & (df['answer'] == 0))]

        ## Very-useful and unclear documents
        if docs.shape[0] < threshold:
            very_useful_unclear_docs = df.loc[(df['usefulness'] == 2) & (df['answer'] == 2)]
            docs = pd.concat([docs, very_useful_unclear_docs])

        ## Useful and unclear documents
        if docs.shape[0] < threshold:
            useful_unclear_docs = df.loc[(df['usefulness'] == 1) & (df['answer'] == 2)]
            docs = pd.concat([docs, useful_unclear_docs])

        final_df = pd.concat([final_df, docs])
    
    final_df.to_csv(save_path + '/pool-detailed.csv', index=False, sep=' ')

    for topic in topic_ids:
        assert (sum(final_df['topic_id'] == topic) >= threshold)
    assert (final_df.usefulness > 0).all()
    assert (final_df.answer >= 0).all()
    assert ((final_df.answer.eq(1) & final_df.topic_answer.eq('Yes')) | (final_df.answer.eq(0) & final_df.topic_answer.eq('No')) | (final_df.answer.eq(2))).all()

    final_pool = final_df[['topic_id', 'doc_no']]
    final_pool.to_csv(save_path + '/pool.csv', index=False, header=False, sep=' ')

    assert ((final_pool.doc_no).eq(final_df.doc_no)).all()

    
    print('[5] Creating file with list of documents to fetch...')
    document_list = final_pool[['doc_no']]
    document_list.to_csv(save_path + '/document_list.csv', index=False, header=False)
    
    assert ((document_list.doc_no).eq(final_df.doc_no)).all()


    print('[6] Complete!')

 