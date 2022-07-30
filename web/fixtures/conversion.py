# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 21:07:13 2022

@author: LinhNhiPM
"""

import pandas as pd
import xml.etree.cElementTree as et
import numpy as np


# Some paths
topics_path = 'C:/Users/LinhNhiPM/Desktop/MMath CS/Research_Ongoing/Thesis/preference-system/judgo/web/fixtures/other-trec-hm-c4-files/conversion-files/input/misinfo-2021-topics.xml'
qrels_path = 'C:/Users/LinhNhiPM/Desktop/MMath CS/Research_Ongoing/Thesis/preference-system/judgo/web/fixtures/other-trec-hm-c4-files/conversion-files/input/qrels-35topics.txt'
save_path = 'C:/Users/LinhNhiPM/Desktop/MMath CS/Research_Ongoing/Thesis/preference-system/judgo/web/fixtures/other-trec-hm-c4-files/conversion-files/output'
#top_n = 10

trec2021_qrels_helpful_path = 'C:/Users/LinhNhiPM/Desktop/MMath CS/Research_Ongoing/Thesis/preference-system/judgo/web/fixtures/other-trec-hm-c4-files/conversion-files/input/misinfo-qrels-graded-helpful-only.txt'
trec2021_qrels_harmful_path = 'C:/Users/LinhNhiPM/Desktop/MMath CS/Research_Ongoing/Thesis/preference-system/judgo/web/fixtures/other-trec-hm-c4-files/conversion-files/input/misinfo-qrels-graded-harmful-only.txt'
    
trec2021_topic_ids = ['101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '114', '115', '117', '118', '120', 
             '121', '122', '127', '128', '129', '131', '132', '133', '134', '136', '137', '139', '140', '143', '144', '145', '146', '149']


if __name__ == '__main__':
    print('[1] Reading from the topics file ...')
    topics_head = ['topic_id', 'query', 'question', 'background', 'disclaimer', 'stance', 'evidence']
    xml_root = et.parse(topics_path)
    rows = xml_root.findall('topic')
    xml_data = [[(row.find('number').text), row.find('query').text, row.find('description').text, row.find('narrative').text,
                 row.find('disclaimer').text, row.find('stance').text, row.find('evidence').text] for row in rows]
    topics = pd.DataFrame(xml_data, columns=topics_head)
    
    
    print('[2] Reading qrels files...')
    qrel = pd.read_csv(qrels_path, header=0, sep=' ',
                       names=['topic_id', 'useless', 'doc_no', 'usefulness', 'supportiveness', 'credibility'],
                       dtype={'topic_id' : np.int64})
    
    helpful_qrel = pd.read_csv(trec2021_qrels_helpful_path, header=0, sep=' ',
                               names=['topic_id', 'useless', 'doc_no', 'score'],
                               dtype={'topic_id': np.int64})
    
    harmful_qrel = pd.read_csv(trec2021_qrels_harmful_path, header=0, sep=' ',
                               names=['topic_id', 'useless', 'doc_no', 'score'],
                               dtype={'topic_id': np.int64})
    
    
    print('[3] Creating questions file...')
    questions = topics[topics['topic_id'].isin(trec2021_topic_ids)]
    questions = questions[['topic_id', 'question', 'background']]
    questions = pd.DataFrame(np.repeat(questions.values, 2, axis=0), columns=questions.columns)
    
    for i, row in questions.iterrows():
        if(i % 2 == 0):
            questions.at[i, 'topic_id'] = questions['topic_id'][i] + '_no'
        else:
            questions.at[i, 'topic_id'] = questions['topic_id'][i] + '_yes'
    
    questions.to_csv(save_path + '/questions.csv', index=False, header=False, sep=' ')
    
    
    print('[4] Creating pools file...')
    help_harm_merged = pd.merge(helpful_qrel, harmful_qrel, how='outer')
    filtered_qrel = qrel.loc[qrel['supportiveness'].isin([0,2])]
    
    pool = pd.merge(help_harm_merged, filtered_qrel, how='inner', on=['topic_id','doc_no'])
    pool = pool[['topic_id', 'doc_no', 'supportiveness']]
    
    for i, row in pool.iterrows():
        if (pool['supportiveness'][i] == 0):
            pool.at[i, 'topic_id'] = str(pool['topic_id'][i]) + '_no'
        else:
            pool.at[i, 'topic_id'] = str(pool['topic_id'][i]) + '_yes'
  
    pool = pool.sort_values(by='topic_id')
    final_pool = pool[['topic_id', 'doc_no']]
    
    final_pool.to_csv(save_path + '/pool.out', index=False, header=False, sep=' ')
    
    
    print('[5] Creating file with list of documents to fetch...')
    document_list = final_pool[['doc_no']]
    
    document_list.to_csv(save_path + '/document_list.csv', index=False, header=False)
    
