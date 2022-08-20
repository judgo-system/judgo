# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 21:07:13 2022

@author: LinhNhiPM
"""

import pandas as pd
import xml.etree.cElementTree as et
import numpy as np


# Some paths
topics_path = '/Users/lnphanmi/Desktop/Thesis/trec2021/trec2021-pref-judge-conversion/input/misinfo-2021-topics.xml'
qrels_path = '/Users/lnphanmi/Desktop/Thesis/trec2021/trec2021-pref-judge-conversion/input/qrels-35topics.txt'
save_path = '/Users/lnphanmi/Desktop/Thesis/trec2021/trec2021-pref-judge-conversion/output'

topic_ids = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114, 115, 117, 118, 120, 
             121, 122, 127, 128, 129, 131, 132, 133, 134, 136, 137, 139, 140, 143, 144, 145, 146, 149]

#threshold = k
threshold = 10

if __name__ == '__main__':
    print('[1] Reading from the topics file ...')
    topics_head = ['topic_id', 'query', 'question', 'background', 'disclaimer', 'stance', 'evidence']
    xml_root = et.parse(topics_path)
    rows = xml_root.findall('topic')
    xml_data = [[int(row.find('number').text), row.find('query').text, row.find('description').text, row.find('narrative').text,
                 row.find('disclaimer').text, row.find('stance').text, row.find('evidence').text] for row in rows]
    topics = pd.DataFrame(xml_data, columns=topics_head)
    
    
    print('[2] Reading qrels files...')
    qrel = pd.read_csv(qrels_path, header=0, sep=' ',
                       names=['topic_id', 'useless', 'doc_no', 'usefulness', 'supportiveness', 'credibility'],
                       dtype={'topic_id' : np.int64})
    
    
    print('[3] Creating questions file...')
    questions = topics[topics['topic_id'].isin(topic_ids)]
    
    for i, row in questions.iterrows():            
        questions.at[i, 'question'] = questions['question'][i] + ' (Answer is ' + questions['stance'][i] + ')'
    
    final_questions = questions[['topic_id', 'question', 'background']]
    final_questions.to_csv(save_path + '/questions.csv', index=False, header=False, sep=' ')
    
    
    print('[4] Creating pools file...')
    topics_truncated = topics[['topic_id' , 'stance']]
    filtered_qrel = qrel.loc[qrel['usefulness'].isin([1,2])]
    filtered_qrel = filtered_qrel.loc[qrel['supportiveness'].isin([0,1,2])]
    filtered_qrel = pd.merge(filtered_qrel, topics_truncated, how='left', on='topic_id')

    final_df = pd.DataFrame(columns=['topic_id', 'useless', 'doc_no', 'usefulness', 'supportiveness', 'credibility', 'stance'])
    for topic in topic_ids:
        df = filtered_qrel.loc[filtered_qrel['topic_id'] == topic]

        # Very-useful and correct documents
        docs = df.loc[(df['usefulness'] == 2) & (((df['stance'] == 'helpful') & (df['supportiveness'] == 2)) | ((df['stance'] == 'unhelpful') & (df['supportiveness'] == 0)))]

        # Useful and correct documents
        if docs.shape[0] < threshold:
            useful_correct_docs = df.loc[(df['usefulness'] == 1) & (((df['stance'] == 'helpful') & (df['supportiveness'] == 2)) | ((df['stance'] == 'unhelpful') & (df['supportiveness'] == 0)))]
            docs = pd.concat([docs, useful_correct_docs])

        # Very-useful and unclear documents
        if docs.shape[0] < threshold:
            very_useful_unclear_docs = df.loc[(df['usefulness'] == 2) & (df['supportiveness'] == 1)]
            docs = pd.concat([docs, very_useful_unclear_docs])

        # Useful and unclear documents
        if docs.shape[0] < threshold:
            useful_unclear_docs = df.loc[(df['usefulness'] == 1) & (df['supportiveness'] == 1)]
            docs = pd.concat([docs, useful_unclear_docs])

        final_df = pd.concat([final_df, docs])
    
    final_pool = final_df[['topic_id', 'doc_no']]
    final_pool.to_csv(save_path + '/pool.csv', index=False, header=False, sep=' ')

    
    print('[5] Creating file with list of documents to fetch...')
    document_list = final_pool[['doc_no']]
    document_list.to_csv(save_path + '/document_list.csv', index=False, header=False)
    

    print('[6] Complete!')
    
